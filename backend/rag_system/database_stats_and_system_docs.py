"""
Database statistics and system documentation.

This file provides:
  1. Code to report how many files, their names, and total chunks are in the RAG "database"
     (FAISS index + chunks_metadata.pkl).
  2. Full documentation of the system and its workflow.
  3. Documentation of how duplicate files are handled.

Run this file directly to print database stats:
  python database_stats_and_system_docs.py
"""

import os
import pickle
import sys

# Use project config for paths
try:
    from .config import FAISS_INDEX_PATH, METADATA_PATH
except ImportError:
    from config import FAISS_INDEX_PATH, METADATA_PATH  # type: ignore

# Optional: ingestion state path (from rag_pipeline)
INGESTION_STATE_PATH = "ingestion_state.json"


# =============================================================================
# PART 1: CODE TO REPORT DATABASE STATS (files, names, total chunks)
# =============================================================================

def load_metadata():
    """Load the chunks metadata from disk. Returns list of chunk metadata dicts or None if missing."""
    if not os.path.isfile(METADATA_PATH):
        return None
    with open(METADATA_PATH, "rb") as f:
        return pickle.load(f)


def load_faiss_index_info():
    """Load FAISS index and return (num_vectors, dimension) or (None, None) if missing."""
    if not os.path.isfile(FAISS_INDEX_PATH):
        return None, None
    import faiss
    index = faiss.read_index(FAISS_INDEX_PATH)
    return index.ntotal, index.d


def get_database_stats():
    """
    Compute and return stats about the RAG "database":
      - total_chunks: total number of chunks (vectors) in the index
      - num_files: number of unique source files
      - file_details: list of dicts with keys: source_file, folder_path, chunk_count, source_path (if present)
    """
    meta = load_metadata()
    if meta is None or not isinstance(meta, list):
        return {
            "index_exists": False,
            "total_chunks": 0,
            "num_files": 0,
            "file_details": [],
            "faiss_vectors": None,
            "faiss_dim": None,
        }

    # Aggregate by unique (source_file, folder_path) or by source_path if available
    file_to_chunks: dict[tuple, list] = {}
    for m in meta:
        if not isinstance(m, dict):
            continue
        # Prefer source_path for uniqueness if present (handles same name in different folders)
        key = (m.get("source_path") or m.get("source_file", ""), m.get("folder_path", ""))
        if key not in file_to_chunks:
            file_to_chunks[key] = []
        file_to_chunks[key].append(m)

    file_details = []
    for (src_path_or_name, folder_path), chunks in sorted(file_to_chunks.items(), key=lambda x: (x[0][0], x[0][1])):
        first = chunks[0] if chunks else {}
        display_name = first.get("source_file") or os.path.basename(str(src_path_or_name)) or "(unknown)"
        file_details.append({
            "source_file": display_name,
            "chunk_count": len(chunks),
        })

    nvec, dim = load_faiss_index_info()
    return {
        "index_exists": nvec is not None,
        "total_chunks": len(meta),
        "num_files": len(file_details),
        "file_details": file_details,
        "faiss_vectors": nvec,
        "faiss_dim": dim,
    }


def print_database_stats():
    """Print a human-readable summary of the database (files, names, total chunks)."""
    stats = get_database_stats()
    print("=" * 60)
    print("RAG DATABASE STATISTICS")
    print("=" * 60)
    if not stats["index_exists"]:
        print("No index found. Run:  python main.py --ingest <folder(s)>")
        print("Metadata path:", METADATA_PATH)
        print("FAISS index path:", FAISS_INDEX_PATH)
        return
    print(f"Total chunks (vectors) in index : {stats['total_chunks']}")
    if stats.get("faiss_vectors") is not None and stats["faiss_vectors"] != stats["total_chunks"]:
        print(f"FAISS index vector count        : {stats['faiss_vectors']}")
    if stats.get("faiss_dim") is not None:
        print(f"Embedding dimension              : {stats['faiss_dim']}")
    print(f"Number of unique source files    : {stats['num_files']}")
    print()
    print("Files and chunk counts:")
    print("-" * 60)
    for i, f in enumerate(stats["file_details"], 1):
        print(f"  {i}. {f['source_file']}")
        print(f"     Chunks: {f['chunk_count']}")
    print("=" * 60)


if __name__ == "__main__":
    print_database_stats()
    sys.exit(0)


# =============================================================================
# PART 2: SYSTEM OVERVIEW AND WORKFLOW
# =============================================================================
"""
RAG SYSTEM — OVERVIEW AND WORKFLOW
----------------------------------

This project is a Retrieval-Augmented Generation (RAG) system. It lets you:
  • Ingest documents (PDF, DOCX, TXT) from folders
  • Ask questions in natural language and get answers grounded in those documents
  • See which source files and pages were used to answer

Components:
  • main.py          — CLI entrypoint: --ingest <folders> and --query "<question>"
  • rag_pipeline.py  — Core pipeline: extraction, chunking, embedding, FAISS, retrieval, rerank, generation
  • config.py        — Configuration (paths, model names, chunk/retrieval settings)
  • service_account.json — GCP credentials for Vertex AI (embeddings + Gemini). Not in git.
  • .env             — Optional env vars (e.g. GEMINI_API_KEY). Not in git.

"Database" in this context means:
  • bank_rag.index       — FAISS vector index (one vector per chunk)
  • chunks_metadata.pkl  — List of metadata dicts (one per chunk): text, source_file, folder_path, page_number, etc.
  • ingestion_state.json — Persistent state used to skip unchanged files on re-ingest (see duplicate handling below).


WORKFLOW
--------

1) INGEST (build or update the index)
   Command:  python main.py --ingest <folder1> [folder2 ...]
   • Scans folder(s) recursively for .pdf, .docx, .txt.
   • For each file: extracts text (and tables for PDF/DOCX), splits into blocks (e.g. per page).
   • Blocks are chunked into overlapping sentence-based chunks (NLTK), with configurable size/overlap.
   • Each chunk is embedded via Vertex AI (gemini-embedding-001).
   • Vectors are stored in a FAISS index (IndexFlatIP, L2-normalized for cosine similarity).
   • Chunk metadata (and text) are stored in chunks_metadata.pkl.
   • Ingestion state (file fingerprints) is written to ingestion_state.json for future runs.

2) QUERY (answer a question)
   Command:  python main.py --query "Your question?"
   • Loads the FAISS index and metadata.
   • Embeds the question with Vertex AI (RETRIEVAL_QUERY task).
   • Retrieves top-K candidate chunks by similarity (FAISS).
   • Re-ranks candidates with TF-IDF (pure Python) to get the best chunks.
   • Chunks are sorted by document order (source_file, page_number, chunk_id) so lists stay coherent.
   • A prompt is built with context from these chunks (with [Source: file, page] labels).
   • Vertex AI Gemini generates an answer from that context only; citations are returned.


DATA FLOW (simplified)
  Documents → Extract (PDF/DOCX/TXT) → Blocks → Chunk (NLTK sentences) → Embed (Vertex AI)
       → FAISS index + metadata.pkl
  Query → Embed query → FAISS search → Rerank → Sort by doc order → Build prompt → Gemini → Answer + citations
"""


# =============================================================================
# PART 3: HOW DUPLICATE FILES ARE HANDLED
# =============================================================================
"""
DUPLICATE FILES — HOW THEY ARE DEALT WITH
-----------------------------------------

The system handles "duplicates" at two levels: within a single run, and across multiple runs.


A) WITHIN A SINGLE INGEST RUN (same run, same folder scan)
   • When you run --ingest folder1 folder2, the code collects all supported files from those folders.
   • Deduplication is by ABSOLUTE FILE PATH: each file path is added to a set; if the same path appears
     again (e.g. from overlapping folder roots), it is skipped. So the same file is never processed twice
     in one run.
   • Implemented in: collect_files_from_folders() in rag_pipeline.py (seen set by abs_path).


B) ACROSS MULTIPLE INGEST RUNS (re-running --ingest on the same or expanded folders)
   • The system keeps a persistent state file: ingestion_state.json.
   • For each file that has ever been successfully ingested, we store a FINGERPRINT (SHA-256 hash of
     file content, plus size and mtime). The key is the file’s absolute path.
   • On every --ingest:
     - We scan the requested folders and compute the current fingerprint for each file.
     - We compare with the stored fingerprint (by absolute path).
     - UNCHANGED FILES: Same path and same SHA-256 → we do NOT re-chunk or re-embed them. They are
       skipped. So duplicate work (and duplicate vectors) from unchanged files is avoided.
     - NEW FILES: Path not in state (or never ingested) → we chunk and embed them, then APPEND
       their vectors to the existing FAISS index and append their metadata to chunks_metadata.pkl.
       No duplicate vectors are created for the same file because we only add new files.
     - CHANGED FILES: Path was in state but SHA-256 changed (file was modified) → we do a FULL
       REBUILD of the index from scratch using all current files in the scanned folders. This
       removes stale vectors and avoids having two versions of the same file in the index (which
       would be “duplicate” content in a sense). We do not support deleting a single file’s vectors
       from FAISS, so a full rebuild is the safe way to reflect changes and avoid duplicates.
   • Summary:
     - Same file, same content, run again → skipped (no duplicate chunks/vectors).
     - Same file, content changed → full rebuild so the index has one up-to-date version.
     - New file added → only that file is processed and appended; no duplication of existing data.

   Implemented in: build_index() and helpers _load_ingestion_state(), _save_ingestion_state(),
   _file_fingerprint(), _sha256_file() in rag_pipeline.py.


C) WHAT IS NOT TREATED AS "DUPLICATE"
   • Two different files with the same name in different folders are two different paths, so both
     are ingested (no content-based deduplication). If you need to avoid ingesting identical content
     under different paths, that would require content-hash–based deduplication across paths, which
     is not implemented here.
"""
