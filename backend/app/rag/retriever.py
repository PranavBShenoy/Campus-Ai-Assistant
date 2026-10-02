import logging
from app.rag.vector_store import get_vector_store
from app.schemas.chat import SourceReference

logger = logging.getLogger('campus_ai.rag.retriever')

class RAGRetriever:
    async def retrieve(self, query: str, user_id: str, top_k: int = None, threshold: float = None) -> list[SourceReference]:
        try:
            store = get_vector_store()
            results = await store.search(query, user_id, top_k, threshold)
            
            sources = []
            seen_chunks = set()

            # Keep multiple distinct chunks from the same file. Question banks and
            # long notes commonly need several chunks to answer one prompt.
            for res in results:
                chunk_id = res['chunk_id']
                if chunk_id not in seen_chunks:
                    seen_chunks.add(chunk_id)
                    sources.append(
                        SourceReference(
                            document_id=res['document_id'],
                            document_name=res['document_name'],
                            excerpt=res['excerpt'][:2000],
                            page_number=res.get('page_number'),
                            chunk_id=res['chunk_id'],
                            relevance_score=res['relevance_score']
                        )
                    )
                    
            return sources
        except Exception as e:
            logger.error(f"Error during retrieval: {str(e)}")
            raise

    async def retrieve_with_context(self, query: str, user_id: str, conversation_history: list[dict]) -> tuple[list[SourceReference], str]:
        # Simple heuristic to determine if it's a follow-up query
        is_follow_up = False
        pronouns = ["it", "this", "that", "they", "he", "she"]
        
        words = query.lower().split()
        if len(words) < 5 or any(p in words for p in pronouns):
            if conversation_history:
                is_follow_up = True
                
        standalone_query = query
        if is_follow_up:
            # A very simplistic reformulation taking last human message context
            last_human_msg = None
            for msg in reversed(conversation_history):
                if msg.get("role") == "user":
                    last_human_msg = msg.get("content")
                    break
            
            if last_human_msg:
                standalone_query = f"{last_human_msg} - {query}"
        
        sources = await self.retrieve(standalone_query, user_id)
        return sources, standalone_query

    def build_context_string(self, sources: list[SourceReference]) -> str:
        if not sources:
            return "No relevant documents found."
            
        context_parts = []
        for i, source in enumerate(sources):
            part = f"--- Source {i+1} ---\n"
            part += f"Document: {source.document_name}\n"
            if source.page_number is not None:
                part += f"Page: {source.page_number}\n"
            part += f"Content: {source.excerpt}\n"
            context_parts.append(part)
            
        return "\n".join(context_parts)
