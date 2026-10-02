import logging
import hashlib
import math
import re
from langchain_core.embeddings import Embeddings
from app.core.config import settings

logger = logging.getLogger('campus_ai.rag.embeddings')


class LocalHashEmbeddings(Embeddings):
    """Offline local fallback used only when the configured model cannot load."""
    dimensions = 384

    def _embed(self, text: str) -> list[float]:
        vector = [0.0] * self.dimensions
        tokens = re.findall(r"[a-z0-9]+", text.lower())
        for token in tokens:
            digest = hashlib.blake2b(token.encode("utf-8"), digest_size=8).digest()
            bucket = int.from_bytes(digest, "big") % self.dimensions
            vector[bucket] += 1.0
        norm = math.sqrt(sum(value * value for value in vector)) or 1.0
        return [value / norm for value in vector]

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        return [self._embed(text) for text in texts]

    def embed_query(self, text: str) -> list[float]:
        return self._embed(text)

class EmbeddingManager:
    _instance = None
    _embeddings = None

    @classmethod
    def get_instance(cls) -> 'EmbeddingManager':
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def get_embeddings(self) -> Embeddings:
        if self._embeddings is None:
            try:
                from langchain_huggingface import HuggingFaceEmbeddings
                logger.info(f"Loading HuggingFace embeddings model: {settings.EMBEDDING_MODEL}")
                self._embeddings = HuggingFaceEmbeddings(
                    model_name=settings.EMBEDDING_MODEL,
                    model_kwargs={"device": "cpu"},
                    encode_kwargs={"normalize_embeddings": True},
                )
            except Exception as e:
                logger.warning("Configured embedding model unavailable; using offline local fallback: %s", e)
                self._embeddings = LocalHashEmbeddings()
        return self._embeddings

    async def embed_texts(self, texts: list[str]) -> list[list[float]]:
        try:
            embeddings = self.get_embeddings()
            return await embeddings.aembed_documents(texts)
        except Exception as e:
            logger.error(f"Error embedding texts: {str(e)}")
            raise

def get_embeddings() -> Embeddings:
    return EmbeddingManager.get_instance().get_embeddings()
