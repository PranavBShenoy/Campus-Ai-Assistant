from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.database.models import Document, Conversation, StudyPlan, Message, DocumentStatus, MessageRole
from app.schemas.dashboard import DashboardStats
from app.schemas.chat import ConversationSummary
from app.schemas.documents import DocumentResponse
import logging

logger = logging.getLogger('campus_ai.api')

class DashboardService:
    async def get_stats(self, user_id: str, db: AsyncSession) -> DashboardStats:
        # Total documents for user
        total_docs_res = await db.execute(
            select(func.count(Document.id)).where(
                Document.user_id == user_id, 
                Document.status != DocumentStatus.deleted
            )
        )
        total_documents = total_docs_res.scalar() or 0
        
        # Total indexed documents for user
        indexed_docs_res = await db.execute(
            select(func.count(Document.id)).where(
                Document.user_id == user_id,
                Document.status == DocumentStatus.indexed
            )
        )
        indexed_documents = indexed_docs_res.scalar() or 0
        
        # Total questions (user messages for user_id)
        questions_res = await db.execute(
            select(func.count(Message.id))
            .join(Conversation, Message.conversation_id == Conversation.id)
            .where(Conversation.user_id == user_id, Message.role == MessageRole.user)
        )
        total_questions = questions_res.scalar() or 0
        
        # Active study plans
        plans_res = await db.execute(
            select(func.count(StudyPlan.id))
            .where(StudyPlan.user_id == user_id, StudyPlan.is_active == True)
        )
        active_study_plans = plans_res.scalar() or 0
        
        # Total conversations
        conv_res = await db.execute(
            select(func.count(Conversation.id)).where(Conversation.user_id == user_id)
        )
        total_conversations = conv_res.scalar() or 0
        
        # Recent 5 conversations
        recent_convs_res = await db.execute(
            select(Conversation)
            .where(Conversation.user_id == user_id)
            .order_by(Conversation.updated_at.desc())
            .limit(5)
        )
        recent_conversations = []
        for c in recent_convs_res.scalars().all():
            try:
                recent_conversations.append(ConversationSummary.model_validate(c, from_attributes=True))
            except Exception as e:
                logger.error(f"Error validating conversation {c.id}: {e}")
        
        # Recent 5 documents
        recent_docs_res = await db.execute(
            select(Document)
            .where(Document.user_id == user_id, Document.status != DocumentStatus.deleted)
            .order_by(Document.upload_date.desc())
            .limit(5)
        )
        recent_documents = []
        for d in recent_docs_res.scalars().all():
            try:
                recent_documents.append(DocumentResponse.model_validate(d, from_attributes=True))
            except Exception as e:
                logger.error(f"Error validating document {d.id}: {e}")
        
        return DashboardStats(
            total_documents=total_documents,
            total_indexed_documents=indexed_documents,
            total_questions=total_questions,
            active_study_plans=active_study_plans,
            total_conversations=total_conversations,
            recent_conversations=recent_conversations,
            recent_documents=recent_documents
        )

