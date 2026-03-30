"""
U-Intelligence Main Application
FastAPI backend for department-specific knowledge assistant
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address
from slowapi.middleware import SlowAPIMiddleware
from app.core.config import settings
from app.core.database import engine, Base
from app.services.rag_service import rag_service  # Initialize RAG service
import logging
import os

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Set specific loggers
logging.getLogger("app.services.rag_service").setLevel(logging.DEBUG)
logging.getLogger("app.routers").setLevel(logging.DEBUG)

# Rate limiter (shared across routers)
limiter = Limiter(key_func=get_remote_address)

# Log startup information
logger.info(f"Starting {settings.PROJECT_NAME} v{settings.VERSION}")
logger.debug(f"GEMINI_API_KEY configured: {bool(settings.GEMINI_API_KEY)}")
logger.debug(f"RAG Service Status: Enabled={rag_service.enabled}")

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="U-Intelligence API",
    description="Department-specific knowledge assistant for UBL",
    version="1.0.0"
)

# slowapi integration
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Startup event to log RAG service details
@app.on_event("startup")
async def startup_event():
    """Log RAG service initialization details"""
    logger.info("=" * 60)
    logger.info("RAG Service Initialization Details:")
    logger.info(f"  - RAG Enabled: {rag_service.enabled}")
    # Adapter keeps these attributes for compatibility, but they are no longer used.
    logger.info(f"  - Legacy Client: {rag_service.client is not None}")
    logger.info(f"  - Legacy Gemini: {rag_service.gemini_client is not None}")
    logger.info("=" * 60)

# Include routers
from app.routers import departments, chat, upload, conversations
app.include_router(departments.router, prefix="/api/departments", tags=["departments"])
app.include_router(chat.router, prefix="/api/chat", tags=["chat"])
app.include_router(upload.router, prefix="/api/upload", tags=["upload"])
app.include_router(conversations.router, prefix="/api/conversations", tags=["conversations"])


@app.get("/")
async def root():
    """Health check endpoint"""
    return {"message": "U-Intelligence API is running", "version": "1.0.0"}


@app.get("/api/health")
async def health_check():
    """Detailed health check"""
    return {
        "status": "healthy",
        "service": "U-Intelligence API",
        "version": "1.0.0",
        "rag_enabled": rag_service.enabled,
        "rag_client": rag_service.client is not None,
        "rag_gemini": rag_service.gemini_client is not None
    }


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler"""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )

