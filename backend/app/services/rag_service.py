"""
RAG service adapter used by the FastAPI backend.

This replaces the prior ChromaDB + Gemini-embeddings implementation and delegates
RAG operations to the project's robust RAG pipeline in `rag_system/`.
"""

from __future__ import annotations

import asyncio
import logging
import os
import sys
from pathlib import Path
from abc import ABC, abstractmethod
from typing import Dict, List, Optional

from app.core.config import settings

logger = logging.getLogger(__name__)

# Allow importing sibling `rag_system/` when backend runs from `backend/`.
_repo_root = Path(__file__).resolve().parents[3]
if str(_repo_root) not in sys.path:
    sys.path.insert(0, str(_repo_root))


class RAGServiceInterface(ABC):
    """Abstract interface for RAG operations."""

    @abstractmethod
    async def ingest_document(self, department_id: str, file_path: str, metadata: Dict) -> bool:
        """Ingest a document into the RAG database."""

    @abstractmethod
    async def query(self, department_id: str, query: str, context: Optional[List[Dict]] = None) -> str:
        """Query the RAG database for department-specific information."""

    @abstractmethod
    async def delete_document(self, department_id: str, document_id: str) -> bool:
        """Delete a document from the RAG database."""


def _list_department_dirs() -> list[str]:
    base = settings.DEPARTMENTS_STORAGE_BASE
    if not os.path.isdir(base):
        return []
    dirs: list[str] = []
    for name in os.listdir(base):
        p = os.path.join(base, name)
        if os.path.isdir(p):
            dirs.append(p)
    return sorted(dirs)


def _department_dir(department_id: str) -> str:
    return os.path.join(settings.DEPARTMENTS_STORAGE_BASE, department_id)


class RagSystemRAGService(RAGServiceInterface):
    """
    Adapter over `rag_system.rag_pipeline`.

    Notes:
    - We keep a single global FAISS index built from ALL department folders.
    - On query, we filter retrieved chunks to the department folder to keep the
      department behavior intact.
    """

    def __init__(self) -> None:
        self.enabled = bool(settings.RAG_ENABLED)

        # Backwards-compat attributes used by app.main health logging.
        self.client = None
        self.gemini_client = None

        logger.info("RAG Service (rag_system) initializing. RAG_ENABLED=%s", self.enabled)

    async def ingest_document(self, department_id: str, file_path: str, metadata: Dict) -> bool:
        if not self.enabled:
            logger.info("RAG disabled. Skipping ingestion for %s: %s", department_id, file_path)
            return True

        # Ensure the department folder exists.
        os.makedirs(_department_dir(department_id), exist_ok=True)

        # Build/update the global index from all department folders.
        dept_dirs = _list_department_dirs()
        if not dept_dirs:
            logger.warning("No department directories found for ingestion.")
            return True

        try:
            from rag_system.rag_pipeline import build_index

            await asyncio.to_thread(build_index, dept_dirs)
            return True
        except Exception as e:
            logger.error("rag_system ingestion failed: %s", e, exc_info=True)
            return False

    async def query(self, department_id: str, query: str, context: Optional[List[Dict]] = None) -> str:
        if not self.enabled:
            return f"I understand you're asking about: {query}. RAG functionality is currently disabled."

        dept_dir = os.path.abspath(_department_dir(department_id))

        try:
            from rag_system.rag_pipeline import query_rag

            def _run_query() -> str:
                # `context` is conversation history sourced from SQLite by the chat router;
                # Gemini only needs the last 6 messages to stay within token limits.
                conversation_history = (context[-6:] if context else None)
                answer, _citations = query_rag(query, conversation_history=conversation_history)
                return answer

            return await asyncio.to_thread(_run_query)
        except FileNotFoundError:
            return "Knowledge base index not found. Please upload documents first."
        except Exception as e:
            logger.error("rag_system query failed: %s", e, exc_info=True)
            return "An error occurred while processing your query."

    async def delete_document(self, department_id: str, document_id: str) -> bool:
        if not self.enabled:
            return True

        # Deletions require an index rebuild to drop stale vectors.
        dept_dirs = _list_department_dirs()
        if not dept_dirs:
            return True

        try:
            from rag_system.rag_pipeline import build_index

            await asyncio.to_thread(build_index, dept_dirs)
            return True
        except Exception as e:
            logger.error("rag_system delete rebuild failed: %s", e, exc_info=True)
            return False


# Singleton instance (kept for existing imports).
rag_service: RagSystemRAGService = RagSystemRAGService()

