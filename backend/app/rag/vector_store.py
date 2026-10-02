import logging
from collections.abc import Iterable
import chromadb
from chromadb.config import Settings as ChromaSettings
from langchain_community.vectorstores import Chroma
from langchain.schema import Document as LCDocument
from app.core.config import settings
from app.rag.embeddings import get_embeddings

logger = logging.getLogger('campus_ai.rag.vector_store')

class VectorStore:
    def __init__(self):
        try:
            self.client = chromadb.PersistentClient(
                path=settings.CHROMADB_PATH,
                settings=ChromaSettings(anonymized_telemetry=False)
            )
            self.collection_name = settings.CHROMADB_COLLECTION
            logger.info(f"Initialized ChromaDB client at {settings.CHROMADB_PATH}")
        except Exception as e:
            logger.error(f"Failed to initialize ChromaDB client: {str(e)}")
            raise

    def get_langchain_store(self) -> Chroma:
        return Chroma(
            client=self.client,
            collection_name=self.collection_name,
            embedding_function=get_embeddings()
        )

    async def add_documents(self, chunks: list[LCDocument], document_id: str) -> int:
        try:
            if not chunks:
                return 0
                
            store = self.get_langchain_store()
            
            # Generate deterministic or unique IDs for chunks to manage them
            ids = [f"{document_id}_{i}" for i in range(len(chunks))]
            store.add_documents(documents=chunks, ids=ids)
            logger.info(f"Added {len(chunks)} chunks to vector store for document {document_id}")
            return len(chunks)
        except Exception as e:
            logger.error(f"Error adding documents to vector store: {str(e)}")
            raise

    async def delete_document(self, document_id: str) -> int:
        try:
            collection = self.client.get_collection(name=self.collection_name)
            results = collection.get(
                where={"document_id": document_id},
                include=[],
            )
            raw_ids = results.get("ids") if isinstance(results, dict) else None
            ids_to_delete = self._normalise_ids(raw_ids)

            if not ids_to_delete:
                logger.info(f"No chunks found for document {document_id} to delete.")
                return 0

            collection.delete(ids=ids_to_delete)
            logger.info(f"Deleted {len(ids_to_delete)} chunks for document {document_id}")
            return len(ids_to_delete)
        except Exception as e:
            # If collection doesn't exist yet, ignore
            if "does not exist" in str(e).lower():
                return 0
            logger.error(f"Error deleting document {document_id}: {str(e)}")
            raise

    @staticmethod
    def _normalise_ids(raw_ids) -> list[str]:
        """Handle Chroma result shapes without ever calling len() on a scalar."""
        if raw_ids is None:
            return []
        if isinstance(raw_ids, (str, int)):
            return [str(raw_ids)]
        if not isinstance(raw_ids, Iterable):
            return [str(raw_ids)]

        normalised = []
        for value in raw_ids:
            if isinstance(value, (list, tuple)):
                normalised.extend(str(item) for item in value)
            elif value is not None:
                normalised.append(str(value))
        return normalised

    async def search(self, query: str, user_id: str, top_k: int = None, threshold: float = None) -> list[dict]:
        try:
            top_k = settings.RAG_TOP_K if top_k is None else top_k
            threshold = settings.RAG_SIMILARITY_THRESHOLD if threshold is None else threshold
            
            store = self.get_langchain_store()
            
            # Use similarity search with score
            filter_kwargs = {"user_id": user_id} if user_id else None
            results = store.similarity_search_with_relevance_scores(
                query, k=top_k, filter=filter_kwargs
            )
            
            formatted_results = []
            for doc, score in results:
                if score >= threshold:
                    formatted_results.append({
                        "document_id": doc.metadata.get("document_id", ""),
                        "document_name": doc.metadata.get("document_name", "Unknown"),
                        "excerpt": doc.page_content,
                        "page_number": doc.metadata.get("page"),
                        "chunk_id": f"{doc.metadata.get('document_id', '')}_{doc.metadata.get('chunk_index', 0)}",
                        "relevance_score": float(score)
                    })
                    
            return formatted_results
        except Exception as e:
            logger.error(f"Error searching vector store: {str(e)}")
            raise

# Singleton pattern
_vector_store = None

def get_vector_store() -> VectorStore:
    global _vector_store
    if _vector_store is None:
        _vector_store = VectorStore()
    return _vector_store
