from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.init_db import get_db
from app.api.deps import get_current_user
from app.database.models import User
from app.schemas.documents import DocumentResponse, DocumentSearchRequest, DocumentSearchResponse
from app.services.document_service import DocumentService

router = APIRouter()
doc_service = DocumentService()

@router.post("/upload", response_model=DocumentResponse)
async def upload_document(
    file: UploadFile = File(...), 
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return await doc_service.upload_document(file, current_user.id, db)

@router.get("/", response_model=list[DocumentResponse])
async def list_documents(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return await doc_service.get_documents(current_user.id, db)

@router.delete("/{document_id}")
async def delete_document(
    document_id: str, 
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    deleted = await doc_service.delete_document(document_id, current_user.id, db)
    if not deleted:
        raise HTTPException(status_code=404, detail="Document not found")
    return {"deleted": True}

@router.post("/{document_id}/reindex", response_model=DocumentResponse)
async def reindex_document(
    document_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    document = await doc_service.reindex_document(document_id, current_user.id, db)
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    return document

@router.post("/search", response_model=DocumentSearchResponse)
async def search_documents(
    request: DocumentSearchRequest, 
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return await doc_service.search_documents(request.query, current_user.id, request.top_k, db)
