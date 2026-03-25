"""
RAG system configuration. All constants and model names.

Note: this module is imported by the FastAPI backend, so resolve file paths
relative to this file (not the backend's working directory).
"""

from pathlib import Path

from dotenv import load_dotenv

RAG_SYSTEM_DIR = Path(__file__).resolve().parent

# Load rag_system/.env explicitly (separate from backend/.env).
load_dotenv(RAG_SYSTEM_DIR / ".env", override=True)

# Vertex AI / GCP config
GCP_PROJECT_ID = "circular-maxim-462609-i6"
GCP_LOCATION = "us-central1"
SERVICE_ACCOUNT_PATH = str(RAG_SYSTEM_DIR / "service_account.json")

GENERATION_MODEL = "gemini-2.5-flash"
EMBEDDING_MODEL = "gemini-embedding-001"
EMBEDDING_DIM = 1536

# Chunking (sentence-based); larger chunks reduce mid-list splits in handbooks/policies
CHUNK_SIZE = 50  # sentences per chunk
CHUNK_OVERLAP = 5  # sentence overlap between chunks

# Retrieval and re-ranking
TOP_K_RETRIEVAL = 30  # FAISS candidates before re-ranking
TOP_K_RERANK = 12  # final chunks passed to the LLM (in doc order for complete lists)

# Persistence (store alongside rag_system code)
FAISS_INDEX_PATH = str(RAG_SYSTEM_DIR / "bank_rag.index")
METADATA_PATH = str(RAG_SYSTEM_DIR / "chunks_metadata.pkl")

# Embedding batching
BATCH_SIZE = 100  # embedding batch size

# Re-ranker model
RERANKER_MODEL = "cross-encoder/ms-marco-MiniLM-L-6-v2"

# Supported file extensions
SUPPORTED_EXTENSIONS = {".pdf", ".docx", ".txt", ".xlsx", ".xls"}

# Minimum chunk length (skip garbage)
MIN_CHUNK_LENGTH = 30

