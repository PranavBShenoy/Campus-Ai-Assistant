from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from app.database.models import DocumentStatus

class DocumentResponse(BaseModel):
    model_config = {'from_attributes': True, 'use_enum_values': True}
    id: str
    filename: str
    original_filename: str
    file_type: str
    file_size: int
    status: DocumentStatus
    error_message: Optional[str] = None
    chunk_count: Optional[int] = None
    upload_date: datetime
    processed_date: Optional[datetime] = None

class DocumentSearchResult(BaseModel):
    document_id: str
    document_name: str
    excerpt: str
    page_number: Optional[int] = None
    chunk_id: str
    relevance_score: float

class DocumentSearchRequest(BaseModel):
    query: str = Field(min_length=1, max_length=1000)
    top_k: int = Field(default=5, ge=1, le=20)

class DocumentSearchResponse(BaseModel):
    results: List[DocumentSearchResult]
    query: str
    total_found: int
