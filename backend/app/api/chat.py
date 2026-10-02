from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.init_db import get_db
from app.database.models import User
from app.api.deps import get_current_user
from app.schemas.chat import ChatRequest, ChatResponse, ConversationSummary, ConversationDetail
from app.services.chat_service import ChatService

router = APIRouter()
chat_service = ChatService()

@router.post("/", response_model=ChatResponse)
async def chat(
    request: ChatRequest, 
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return await chat_service.send_message(request, current_user.id, db)

@router.get("/conversations", response_model=list[ConversationSummary])
async def list_conversations(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return await chat_service.get_conversations(current_user.id, db)

@router.get("/conversations/{conversation_id}", response_model=ConversationDetail)
async def get_conversation(
    conversation_id: str, 
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    conversation = await chat_service.get_conversation(conversation_id, current_user.id, db)
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return conversation

@router.delete("/conversations/{conversation_id}")
async def delete_conversation(
    conversation_id: str, 
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    deleted = await chat_service.delete_conversation(conversation_id, current_user.id, db)
    if not deleted:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return {"deleted": True}
