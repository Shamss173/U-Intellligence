"""
One-time migration: convert `chunks_metadata.pkl` to `metadata.db` (SQLite).

This avoids re-running embeddings/FAISS ingest when only metadata storage changed.
"""

from __future__ import annotations

import argparse
import os
import pickle
import sqlite3
from pathlib import Path


def main() -> None:
    base_dir = Path(__file__).resolve().parent
    metadata_pkl_path = base_dir / "chunks_metadata.pkl"
    metadata_db_path = base_dir / "metadata.db"

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--force",
        action="store_true",
        help="Overwrite metadata.db if it already exists.",
    )
    args = parser.parse_args()

    if not metadata_pkl_path.is_file():
        raise FileNotFoundError(f"Missing pickle metadata: {metadata_pkl_path}")

    if metadata_db_path.exists() and not args.force:
        print(f"metadata.db already exists at {metadata_db_path}. Use --force to overwrite.")
        return

    conn = sqlite3.connect(str(metadata_db_path))
    conn.row_factory = sqlite3.Row

    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS chunks (
            chunk_id INTEGER PRIMARY KEY,
            text TEXT,
            source_file TEXT,
            folder_path TEXT,
            department_id TEXT,
            page_number INTEGER,
            file_type TEXT,
            source_path TEXT,
            relative_path TEXT
        )
        """
    )

    if args.force:
        conn.execute("DELETE FROM chunks")

    with open(str(metadata_pkl_path), "rb") as f:
        metadata_list = pickle.load(f)

    if not isinstance(metadata_list, list):
        raise ValueError("Pickle did not contain a list of metadata dicts.")

    rows: list[tuple] = []
    for m in metadata_list:
        if not isinstance(m, dict):
            continue
        if "chunk_id" not in m:
            continue
        chunk_id = int(m.get("chunk_id"))
        rows.append(
            (
                chunk_id,
                m.get("text", "") or "",
                m.get("source_file", "") or "",
                m.get("folder_path", "") or "",
                m.get("department_id"),
                m.get("page_number"),
                m.get("file_type", "") or "",
                m.get("source_path"),
                m.get("relative_path"),
            )
        )

    sql = """
        INSERT OR REPLACE INTO chunks (
            chunk_id,
            text,
            source_file,
            folder_path,
            department_id,
            page_number,
            file_type,
            source_path,
            relative_path
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """

    if rows:
        conn.executemany(sql, rows)

    conn.commit()
    conn.close()

    print(f"Migrated {len(rows)} chunk metadata rows into {metadata_db_path}")


if __name__ == "__main__":
    main()

