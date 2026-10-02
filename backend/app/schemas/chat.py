from pydantic import BaseModel, Field
from typing import Optional, Literal, List
from datetime import datetime

class SourceReference(BaseModel):
    document_id: str
    document_name: str
    excerpt: str = Field(..., max_length=2000)
    page_number: Optional[int] = None
    chunk_id: str
    relevance_score: float

class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=10000)
    conversation_id: Optional[str] = None
    mode: Literal['basic_llm', 'academic_rag']
    session_id: Optional[str] = None

class ChatResponse(BaseModel):
    model_config = {'from_attributes': True, 'use_enum_values': True}
    conversation_id: str
    message_id: str
    response: str
    sources: List[SourceReference] = []
    mode: str
    processing_time_ms: float
    tokens_used: Optional[int] = None
    intent: Optional[str] = None

class ConversationSummary(BaseModel):
    model_config = {'from_attributes': True, 'use_enum_values': True}
    id: str
    title: str
    created_at: datetime
    updated_at: datetime
    message_count: int
    mode: str

class MessageSchema(BaseModel):
    model_config = {'from_attributes': True, 'use_enum_values': True}
    id: str
    role: str
    content: str
    sources: Optional[List[SourceReference]] = None
    mode: str
    created_at: datetime

class ConversationDetail(BaseModel):
    model_config = {'from_attributes': True, 'use_enum_values': True}
    id: str
    title: str
    messages: List[MessageSchema]
    created_at: datetime
    updated_at: datetime


