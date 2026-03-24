"""
Application configuration
"""
from pathlib import Path
try:
    from pydantic_settings import BaseSettings
except ImportError:
    from pydantic import BaseSettings
from typing import List
import os
import logging
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

# Load .env file explicitly from backend directory
backend_dir = Path(__file__).parent.parent.parent  # Go up to backend directory
env_file = backend_dir / ".env"
if env_file.exists():
    load_dotenv(env_file, override=True)
else:
    logger.warning(f".env not found at: {env_file}")

# Get values from environment (which were loaded from .env)
_gemini_api_key_from_env = os.getenv("GEMINI_API_KEY", "")
_rag_enabled_from_env = os.getenv("RAG_ENABLED", "True").lower() in ("true", "1", "yes")


class Settings(BaseSettings):
    """Application settings"""
    PROJECT_NAME: str = "U-Intelligence"
    VERSION: str = "1.0.0"
    
    # Database
    DATABASE_URL: str = "sqlite:///./u_intelligence.db"
    
    # CORS
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
    ]
    
    # File upload
    UPLOAD_DIR: str = "./uploads"
    MAX_UPLOAD_SIZE: int = 50 * 1024 * 1024  # 50MB
    ALLOWED_EXTENSIONS: List[str] = [".pdf", ".docx", ".txt", ".doc"]
    
    # RAG Configuration - Read from environment
    RAG_ENABLED: bool = _rag_enabled_from_env
    
    # RAG Model Provider Configuration
    # Options: "openai", "anthropic", "local", "azure", "google"
    RAG_MODEL_PROVIDER: str = "google"  # Using Google Gemini
    
    # Embedding Model Configuration
    # For Google: "models/gemini-embedding-001"
    RAG_EMBEDDING_MODEL: str = "models/gemini-embedding-001"
    
    # Vector Database Configuration
    # Using Chroma as the vector database
    RAG_VECTOR_DB: str = "chroma"
    RAG_VECTOR_DB_PATH: str = "./my_vector_db_v2"
    
    # Vector Database Connection (if needed)
    RAG_VECTOR_DB_URL: str = ""
    RAG_VECTOR_DB_API_KEY: str = ""
    
    # LLM Configuration for RAG
    RAG_LLM_MODEL: str = "gemini-2.5-flash"  # Using Gemini 2.5 Flash
    RAG_LLM_TEMPERATURE: float = 0.7
    RAG_LLM_MAX_TOKENS: int = 1000
    
    # RAG Retrieval Configuration
    RAG_TOP_K: int = 5  # Number of relevant chunks to retrieve
    RAG_CHUNK_SIZE: int = 1000  # Character size for document chunks
    RAG_CHUNK_OVERLAP: int = 200  # Overlap between chunks
    
    # Gemini API Key (required for embeddings and LLM)
    GEMINI_API_KEY: str = _gemini_api_key_from_env
    
    # Department-specific storage paths
    DEPARTMENTS_STORAGE_BASE: str = "./department_storage"
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()

# Create necessary directories
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
os.makedirs(settings.DEPARTMENTS_STORAGE_BASE, exist_ok=True)

# Log RAG configuration status
import logging
logger = logging.getLogger(__name__)
logger.info(f"RAG Configuration - Enabled: {settings.RAG_ENABLED}")
logger.info(f"GEMINI_API_KEY loaded: {bool(settings.GEMINI_API_KEY)}")
if settings.GEMINI_API_KEY:
    logger.info(f"GEMINI_API_KEY (first 20 chars): {settings.GEMINI_API_KEY[:20]}")
if settings.RAG_ENABLED:
    logger.info(f"RAG Provider: {settings.RAG_MODEL_PROVIDER}")
    logger.info(f"RAG Vector DB: {settings.RAG_VECTOR_DB}")
    logger.info(f"RAG Vector DB Path: {settings.RAG_VECTOR_DB_PATH}")
    logger.info(f"RAG Embedding Model: {settings.RAG_EMBEDDING_MODEL}")
    logger.info(f"RAG LLM Model: {settings.RAG_LLM_MODEL}")
else:
    logger.info("RAG is disabled. Enable RAG_ENABLED=True in configuration to activate.")
