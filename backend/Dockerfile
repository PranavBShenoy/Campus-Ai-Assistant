FROM python:3.11-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Non-secret environment variables
ENV LLM_PROVIDER=openrouter
ENV OPENROUTER_MODEL=openai/gpt-4o-mini
ENV OPENROUTER_STUDY_PLAN_MODEL=
ENV OPENROUTER_REVIEW_MODEL=

ENV LANGSMITH_TRACING=false
ENV LANGSMITH_PROJECT=campus-ai-dev
ENV LANGSMITH_ENDPOINT=https://api.smith.langchain.com

ENV EMBEDDING_MODEL=all-MiniLM-L6-v2

ENV DATABASE_URL=sqlite+aiosqlite:///./campus_ai.db

ENV CHROMADB_PATH=./data/chroma_db
ENV CHROMADB_COLLECTION=campus_ai_docs

ENV RAG_CHUNK_SIZE=800
ENV RAG_CHUNK_OVERLAP=150
ENV RAG_TOP_K=5
ENV RAG_SIMILARITY_THRESHOLD=0.1
ENV CONVERSATION_HISTORY_WINDOW=10

ENV MAX_FILE_SIZE_MB=50
ENV UPLOAD_DIR=./data/uploads

ENV FRONTEND_URL=https://campus-ai-assistant-bay.vercel.app
ENV API_HOST=0.0.0.0
ENV DEBUG=false
ENV DEMO_MODE=false

ENV ACCESS_TOKEN_EXPIRE_MINUTES=10080

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}"]