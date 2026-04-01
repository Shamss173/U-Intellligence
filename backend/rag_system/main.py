"""
CLI entrypoint for the banking RAG system.
Modes: --ingest (one or more folder paths), --query (single question).
"""
import argparse
import logging
import os
import sys

try:
    from .config import FAISS_INDEX_PATH
    from .rag_pipeline import build_index, query_rag
except ImportError:
    # Allow running as a plain script from this directory.
    from config import FAISS_INDEX_PATH  # type: ignore
    from rag_pipeline import build_index, query_rag  # type: ignore

# Configure logging at INFO level
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)


def run_ingest(folder_paths: list[str]) -> None:
    """Ingest documents from all given folders, build unified FAISS index."""
    if not folder_paths:
        logger.error("No folder paths provided for ingest.")
        sys.exit(1)
    valid = [f for f in folder_paths if os.path.isdir(os.path.abspath(f))]
    for f in folder_paths:
        if f not in valid:
            logger.warning("Folder does not exist, skipping: %s", f)
    if not valid:
        logger.error("No valid folders to ingest.")
        sys.exit(1)
    logger.info("Ingesting from %d folder(s): %s", len(valid), valid)
    build_index(valid)
    if os.path.isfile(FAISS_INDEX_PATH):
        size_mb = os.path.getsize(FAISS_INDEX_PATH) / (1024 * 1024)
        logger.info("Index saved successfully. Index file size: %.2f MB", size_mb)


def run_query(question: str, dept: str = None) -> None:
    """Load index, run RAG pipeline, print answer and citations."""
    if not question or not question.strip():
        logger.error("Empty query.")
        sys.exit(1)
        
    if dept:
        print(f"\n🏢 Department: {dept}")
    else:
        print(f"\n🌐 No department filter — searching all documents")

    print(f"❓ Query: {question}\n")
        
    try:
        answer, citations = query_rag(question.strip(), department_filter=dept)
    except FileNotFoundError as e:
        print("Index not found. Please run --ingest first.", file=sys.stderr)
        logger.warning("%s", e)
        sys.exit(1)
    except Exception as e:
        logger.exception("Query failed: %s", e)
        print("An error occurred while processing your query. Please try again.", file=sys.stderr)
        sys.exit(1)

    print("\n--- Answer ---\n")
    print(answer)
    print("\n--- Sources ---\n")
    seen = set()
    for c in citations:
        key = (c.get("source_file"), c.get("folder_path"), c.get("page_number"))
        if key in seen:
            continue
        seen.add(key)
        page = c.get("page_number")
        page_str = f", page {page}" if page is not None else ""
        print(f"  - {c.get('source_file', '')} ({c.get('folder_path', '')}{page_str})")
    print()


def main() -> None:
    parser = argparse.ArgumentParser(description="Banking RAG: ingest documents or query.")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "--ingest",
        nargs="+",
        metavar="FOLDER",
        help="Ingest documents from one or more folders (recursive).",
    )
    group.add_argument(
        "--query",
        type=str,
        metavar="QUESTION",
        help="Ask a question (requires existing index from --ingest).",
    )
    parser.add_argument(
        "--dept",
        type=str,
        required=False,
        default=None,
        help="Department code e.g. hrg, finance, it, operations_transformation"
    )
    args = parser.parse_args()

    if args.ingest is not None:
        run_ingest(args.ingest)
    else:
        run_query(args.query, args.dept)


if __name__ == "__main__":
    main()
