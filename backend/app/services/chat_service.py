from __future__ import annotations
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from langchain.schema import HumanMessage, AIMessage
from app.database.models import Conversation, Message, ConversationMode, MessageRole
from app.schemas.chat import (
    ChatRequest, ChatResponse, SourceReference,
    ConversationSummary, ConversationDetail, MessageSchema
)
from app.graph.workflow import run_academic_workflow
from app.core.config import settings
import uuid, time, logging
from fastapi import HTTPException, status

logger = logging.getLogger("campus_ai.api")


class ChatService:
    async def send_message(self, request: ChatRequest, user_id: str, db: AsyncSession) -> ChatResponse:
        start_time = time.time()
        conversation = None
        history = []

        if not settings.llm_configured:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="LLM API is not configured.",
            )

        if request.conversation_id:
            result = await db.execute(
                select(Conversation).where(
                    Conversation.id == request.conversation_id,
                    Conversation.user_id == user_id,
                )
            )
            conversation = result.scalar_one_or_none()
            if not conversation:
                raise HTTPException(status_code=404, detail="Conversation not found")
            msgs_result = await db.execute(
                select(Message)
                .where(Message.conversation_id == request.conversation_id)
                .order_by(Message.created_at.desc())
                .limit(settings.CONVERSATION_HISTORY_WINDOW)
            )
            db_messages = list(reversed(msgs_result.scalars().all()))
            for msg in db_messages:
                if msg.role == MessageRole.user:
                    history.append(HumanMessage(content=msg.content))
                elif msg.role == MessageRole.assistant:
                    history.append(AIMessage(content=msg.content))

        if not conversation:
            title = request.message[:50] + "..." if len(request.message) > 50 else request.message
            conversation = Conversation(
                id=str(uuid.uuid4()),
                session_id=request.session_id,
                user_id=user_id,
                title=title,
                mode=ConversationMode(request.mode),
                message_count=0,
            )
            db.add(conversation)
            await db.flush()

        try:
            state = await run_academic_workflow(
                query=request.message,
                mode=request.mode,
                session_id=request.session_id,
                user_id=user_id,
                conversation_id=conversation.id,
                history=history,
            )
        except Exception as exc:
            await db.rollback()
            logger.error("Academic workflow failed", exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="CampusAI could not generate an answer right now. Please try again.",
            ) from exc

        generated_response = state.get("generated_response") or "Error generating response."
        sources_raw = state.get("sources") or []
        conv_mode = ConversationMode(request.mode)

        user_msg = Message(
            id=str(uuid.uuid4()),
            conversation_id=conversation.id,
            role=MessageRole.user,
            content=request.message,
            mode=conv_mode,
        )
        db.add(user_msg)

        assistant_msg_id = str(uuid.uuid4())
        assistant_msg = Message(
            id=assistant_msg_id,
            conversation_id=conversation.id,
            role=MessageRole.assistant,
            content=generated_response,
            sources_json=sources_raw,
            mode=conv_mode,
        )
        db.add(assistant_msg)

        conversation.message_count = (conversation.message_count or 0) + 2
        conversation.mode = conv_mode
        await db.commit()

        sources = []
        for s in sources_raw:
            try:
                sources.append(SourceReference(**s))
            except Exception:
                pass

        return ChatResponse(
            conversation_id=conversation.id,
            message_id=assistant_msg_id,
            response=generated_response,
            sources=sources,
            mode=request.mode,
            processing_time_ms=int((time.time() - start_time) * 1000),
            intent=state.get("intent"),
        )

    async def get_conversations(self, user_id: str, db: AsyncSession) -> list:
        result = await db.execute(
            select(Conversation)
            .where(Conversation.user_id == user_id)
            .order_by(Conversation.updated_at.desc())
            .limit(50)
        )
        convs = result.scalars().all()
        return [ConversationSummary.model_validate(c, from_attributes=True) for c in convs]

    async def get_conversation(self, conversation_id: str, user_id: str, db: AsyncSession) -> Optional[ConversationDetail]:
        result = await db.execute(select(Conversation).where(Conversation.id == conversation_id, Conversation.user_id == user_id))
        conversation = result.scalar_one_or_none()
        if not conversation:
            return None

        msgs_result = await db.execute(
            select(Message)
            .where(Message.conversation_id == conversation_id)
            .order_by(Message.created_at.asc())
        )
        messages = msgs_result.scalars().all()

        msg_schemas = []
        for msg in messages:
            sources = []
            if msg.sources_json:
                for s in msg.sources_json:
                    try:
                        sources.append(SourceReference(**s))
                    except Exception:
                        pass
            msg_schemas.append(MessageSchema(
                id=msg.id,
                role=msg.role.value,
                content=msg.content,
                sources=sources,
                mode=msg.mode.value if msg.mode else "basic_llm",
                created_at=msg.created_at,
            ))

        return ConversationDetail(
            id=conversation.id,
            title=conversation.title,
            messages=msg_schemas,
            created_at=conversation.created_at,
            updated_at=conversation.updated_at,
        )

    async def delete_conversation(self, conversation_id: str, user_id: str, db: AsyncSession) -> bool:
        result = await db.execute(select(Conversation).where(Conversation.id == conversation_id, Conversation.user_id == user_id))
        conversation = result.scalar_one_or_none()
        if not conversation:
            return False
        await db.delete(conversation)
        await db.commit()
        return True

