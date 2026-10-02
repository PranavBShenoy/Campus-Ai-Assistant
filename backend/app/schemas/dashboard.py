from pydantic import BaseModel
from typing import List
from app.schemas.chat import ConversationSummary
from app.schemas.documents import DocumentResponse

class DashboardStats(BaseModel):
    total_documents: int
    total_indexed_documents: int
    total_questions: int
    active_study_plans: int
    total_conversations: int
    recent_conversations: List[ConversationSummary]
    recent_documents: List[DocumentResponse]
