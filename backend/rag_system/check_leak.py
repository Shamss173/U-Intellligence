"""
File: backend/rag_system/check_leak.py
Diagnose exactly what operations_transformation returns
for the data governance query
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from rag_system.rag_pipeline import load_index, retrieve

index, metadata_list = load_index()

chunks = retrieve(
    index, metadata_list,
    "What are the data governance policies?",
    department_filter="operations_transformation"
)

print(f"Total chunks returned: {len(chunks)}\n")
for i, c in enumerate(chunks[:5]):
    print(f"Chunk {i+1}:")
    print(f"  File      : {c['metadata'].get('source_file')}")
    print(f"  Department: {c['metadata'].get('department')}")
    print(f"  Score     : {c.get('score', 'N/A')}")
    print(f"  Preview   : {c['text'][:150]}")
    print()