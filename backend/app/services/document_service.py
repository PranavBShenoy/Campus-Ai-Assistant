from __future__ import annotations
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException, UploadFile, status
from app.database.models import Document, DocumentStatus
from app.schemas.documents import DocumentResponse, DocumentSearchResult, DocumentSearchResponse
from app.rag.document_processor import DocumentProcessor
from app.rag.vector_store import get_vector_store
from app.core.config import settings
from app.database.init_db import async_session_maker
import uuid, aiofiles, os, logging, asyncio
from datetime import datetime

logger = logging.getLogger("campus_ai.api")


class DocumentService:
    async def upload_document(self, file: UploadFile, user_id: str, db: AsyncSession) -> DocumentResponse:
        processor = DocumentProcessor()
        file_content = await file.read()
        file_size = len(file_content)

        valid, error_msg = processor.validate_file(file.filename or "", file_size)
        if not valid:
            from fastapi import HTTPException
            raise HTTPException(status_code=400, detail=error_msg)

        doc_id = str(uuid.uuid4())
        ext = os.path.splitext(file.filename or "")[1].lower()
        file_type = ext.lstrip(".")
        safe_name = processor.get_safe_filename(file.filename or "unknown")
        file_name_on_disk = f"{doc_id}_{safe_name}"
        file_path = os.path.join(settings.UPLOAD_DIR, file_name_on_disk)

        os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
        async with aiofiles.open(file_path, "wb") as out_file:
            await out_file.write(file_content)

        doc = Document(user_id=user_id,
            id=doc_id,
            filename=file_name_on_disk,
            original_filename=file.filename or "unknown",
            file_type=file_type,
            file_size=file_size,
            status=DocumentStatus.uploading,
        )
        db.add(doc)
        await db.commit()
        await db.refresh(doc)

        asyncio.create_task(
            self._process_document(doc.id, user_id, file_path, file.filename or "unknown", file_type)
        )

        return DocumentResponse.model_validate(doc, from_attributes=True)

    async def _process_document(
        self, doc_id: str, user_id: str, file_path: str, original_filename: str, file_type: str
    ) -> None:
        async with async_session_maker() as db:
            try:
                result = await db.execute(select(Document).where(Document.id == doc_id))
                doc = result.scalar_one_or_none()
                if not doc:
                    return
                doc.status = DocumentStatus.processing
                await db.commit()

                processor = DocumentProcessor()
                chunks = await processor.process_document(
                    file_path=file_path,
                    document_id=doc_id,
                    original_filename=original_filename,
                    file_type=file_type,
                    user_id=user_id,
                )
                chunk_count = len(chunks)
                if chunk_count == 0:
                    raise ValueError("No readable text was found in this document.")

                vector_store = get_vector_store()
                # Re-indexing is idempotent: remove stale chunks before adding.
                await vector_store.delete_document(doc_id)
                await vector_store.add_documents(chunks, doc_id)

                result = await db.execute(select(Document).where(Document.id == doc_id))
                doc = result.scalar_one()
                if doc.status == DocumentStatus.deleted:
                    # A delete may race with background indexing. Never leave orphaned
                    # vectors or resurrect a document that the user deleted.
                    await vector_store.delete_document(doc_id)
                    return
                doc.status = DocumentStatus.indexed
                doc.chunk_count = chunk_count
                doc.processed_date = datetime.utcnow()
                await db.commit()
                logger.info(f"Document {doc_id} indexed with {chunk_count} chunks.")

            except Exception as e:
                logger.error(f"Error processing document {doc_id}: {e}", exc_info=True)
                try:
                    result = await db.execute(select(Document).where(Document.id == doc_id))
                    doc = result.scalar_one_or_none()
                    if doc and doc.status != DocumentStatus.deleted:
                        doc.status = DocumentStatus.failed
                        doc.error_message = "This file could not be indexed. Try again or upload a text-based copy."
                        await db.commit()
                except Exception as inner:
                    logger.error(f"Could not update failed status for {doc_id}: {inner}")

    async def get_documents(self, user_id: str, db: AsyncSession) -> list[DocumentResponse]:
        result = await db.execute(
            select(Document)
            .where(
                Document.user_id == user_id,
                Document.status != DocumentStatus.deleted,
            )
            .order_by(Document.upload_date.desc())
        )
        docs = result.scalars().all()
        return [DocumentResponse.model_validate(d, from_attributes=True) for d in docs]

    async def get_document(self, doc_id: str, user_id: str, db: AsyncSession) -> Optional[DocumentResponse]:
        result = await db.execute(
            select(Document).where(Document.id == doc_id, Document.user_id == user_id)
        )
        doc = result.scalar_one_or_none()
        if not doc:
            return None
        return DocumentResponse.model_validate(doc, from_attributes=True)

    async def delete_document(self, doc_id: str, user_id: str, db: AsyncSession) -> bool:
        result = await db.execute(
            select(Document).where(Document.id == doc_id, Document.user_id == user_id)
        )
        doc = result.scalar_one_or_none()
        if not doc:
            return False
        try:
            vector_store = get_vector_store()
            await vector_store.delete_document(doc_id)
        except Exception as e:
            logger.error(f"Error deleting vectors for {doc_id}: {e}", exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Document vector cleanup failed; the document was not deleted.",
            ) from e
        doc.status = DocumentStatus.deleted
        await db.commit()
        try:
            full_path = os.path.join(settings.UPLOAD_DIR, doc.filename)
            if os.path.exists(full_path):
                os.remove(full_path)
        except Exception:
            pass
        return True

    async def reindex_document(self, doc_id: str, user_id: str, db: AsyncSession) -> Optional[DocumentResponse]:
        result = await db.execute(
            select(Document).where(
                Document.id == doc_id,
                Document.user_id == user_id,
                Document.status != DocumentStatus.deleted,
            )
        )
        doc = result.scalar_one_or_none()
        if not doc:
            return None
        file_path = os.path.join(settings.UPLOAD_DIR, doc.filename)
        if not os.path.isfile(file_path):
            raise HTTPException(status_code=404, detail="The uploaded file is no longer available.")
        doc.status = DocumentStatus.processing
        doc.error_message = None
        doc.chunk_count = None
        await db.commit()
        await db.refresh(doc)
        asyncio.create_task(
            self._process_document(doc.id, user_id, file_path, doc.original_filename, doc.file_type)
        )
        return DocumentResponse.model_validate(doc, from_attributes=True)

    async def search_documents(self, query: str, user_id: str, top_k: int, db: AsyncSession) -> DocumentSearchResponse:
        try:
            vector_store = get_vector_store()
            results_raw = await vector_store.search(query, user_id, top_k)
        except Exception as e:
            logger.error(f"Search error: {e}", exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Knowledge base search is currently unavailable.",
            ) from e

        indexed_docs = await db.execute(
            select(Document.id).where(
                Document.user_id == user_id,
                Document.status == DocumentStatus.indexed,
            )
        )
        allowed_document_ids = set(indexed_docs.scalars().all())

        search_results = []
        for r in results_raw:
            if r.get("document_id") not in allowed_document_ids:
                continue
            try:
                search_results.append(DocumentSearchResult(**r))
            except Exception:
                pass

        return DocumentSearchResponse(
            query=query,
            results=search_results,
            total_found=len(search_results),
        )
