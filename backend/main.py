import os
import time
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import logging

from app.core.config import settings
from app.core.logging_config import setup_logging
from app.database.init_db import init_db

setup_logging()
logger = logging.getLogger("campus_ai.main")

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Starting CampusAI backend...")
    
    # Create necessary directories
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    os.makedirs(settings.CHROMADB_PATH, exist_ok=True)
    
    # Initialize DB
    await init_db()
    
    if not settings.llm_configured:
        logger.warning("LLM API Keys not configured. Set DEMO_MODE=true for mock responses.")
    else:
        logger.info(f"LLM configured with provider: {settings.LLM_PROVIDER}")
        
    yield
    # Shutdown
    logger.info("Shutting down CampusAI backend...")

app = FastAPI(
    title="CampusAI API",
    description="Backend for CampusAI educational assistant",
    version="1.0.0",
    lifespan=lifespan
)

# CORS setup
allowed_origins = {
    "http://localhost:3000",
    "http://127.0.0.1:3000",
}
allowed_origins.update(
    origin.strip().rstrip("/")
    for origin in settings.FRONTEND_URL.split(",")
    if origin.strip()
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=sorted(allowed_origins),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Timing middleware
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response

# Error Handlers
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    import traceback; traceback.print_exc(); logger.error(f"Global exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )

from app.api import auth, chat, documents, study_plans, evaluation, dashboard
app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(chat.router, prefix="/api/chat", tags=["chat"])
app.include_router(documents.router, prefix="/api/documents", tags=["documents"])
app.include_router(study_plans.router, prefix="/api/study-plans", tags=["study_plans"])
app.include_router(evaluation.router, prefix="/api/evaluation", tags=["evaluation"])
app.include_router(dashboard.router, prefix="/api/dashboard", tags=["dashboard"])

@app.get("/api/health", tags=["health"])
async def health_check():
    return {
        "status": "ok",
        "llm_configured": settings.llm_configured,
        "demo_mode": settings.DEMO_MODE,
        "version": app.version
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host=settings.API_HOST, port=settings.API_PORT, reload=settings.DEBUG)
