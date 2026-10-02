import os
from pathlib import Path
from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict

BACKEND_DIR = Path(__file__).resolve().parents[2]

class Settings(BaseSettings):
    # LLM Settings
    LLM_PROVIDER: str = "openrouter"
    OPENROUTER_API_KEY: Optional[str] = None
    OPENROUTER_MODEL: str = "openai/gpt-4o-mini" # Default fallback
    OPENROUTER_STUDY_PLAN_MODEL: Optional[str] = None
    OPENROUTER_REVIEW_MODEL: Optional[str] = None
    
    # LangSmith Tracing
    LANGSMITH_TRACING: bool = False
    LANGSMITH_API_KEY: Optional[str] = None
    LANGSMITH_PROJECT: str = "campus-ai-dev"
    LANGSMITH_ENDPOINT: str = "https://api.smith.langchain.com"
    
    # Auth Settings
    SECRET_KEY: str = "supersecret_change_in_production_campus_ai_123!"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days

    # Embeddings
    EMBEDDING_MODEL: str = "all-MiniLM-L6-v2"
    
    # Database
    DATABASE_URL: str = "sqlite+aiosqlite:///./campus_ai.db"
    
    # ChromaDB
    CHROMADB_PATH: str = "./data/chroma_db"
    CHROMADB_COLLECTION: str = "campus_ai_docs"
    
    # RAG Settings
    RAG_CHUNK_SIZE: int = 800
    RAG_CHUNK_OVERLAP: int = 150
    RAG_TOP_K: int = 5
    RAG_SIMILARITY_THRESHOLD: float = 0.1
    CONVERSATION_HISTORY_WINDOW: int = 10
    
    # File Upload
    MAX_FILE_SIZE_MB: int = 50
    UPLOAD_DIR: str = "./data/uploads"
    
    # API
    FRONTEND_URL: str = "http://localhost:3000"
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    DEBUG: bool = True
    
    # Demo Mode
    DEMO_MODE: bool = False

    model_config = SettingsConfigDict(
        env_file=str(BACKEND_DIR / ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @property
    def is_openrouter(self) -> bool:
        return self.LLM_PROVIDER.lower() == "openrouter"
        
    @property
    def llm_configured(self) -> bool:
        if self.DEMO_MODE:
            return True
        if self.is_openrouter and self.OPENROUTER_API_KEY:
            return True
        return False
        
    def setup_langsmith(self):
        if self.LANGSMITH_TRACING:
            os.environ["LANGCHAIN_TRACING_V2"] = "true"
            if self.LANGSMITH_API_KEY:
                os.environ["LANGCHAIN_API_KEY"] = self.LANGSMITH_API_KEY
            os.environ["LANGCHAIN_PROJECT"] = self.LANGSMITH_PROJECT
            os.environ["LANGCHAIN_ENDPOINT"] = self.LANGSMITH_ENDPOINT
        else:
            os.environ["LANGCHAIN_TRACING_V2"] = "false"

settings = Settings()
# Initialize LangSmith settings based on environment
settings.setup_langsmith()
