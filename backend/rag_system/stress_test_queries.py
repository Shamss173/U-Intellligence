"""
File: backend/rag_system/stress_test_queries.py
Tests system behavior on edge case queries
Run: python stress_test_queries.py
"""

import sys
from pathlib import Path

# Add the backend directory to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from rag_system.rag_pipeline import query_rag

STRESS_TESTS = {
    "naive": [
        "Hello",
        "Hi",
        "How are you?",
        "Thanks",
        "What can you do?",
    ]
}

def run_stress_tests():
    print("=" * 65)
    print("U-INTELLIGENCE — STRESS TEST QUERIES")
    print("=" * 65)
    
    for category, queries in STRESS_TESTS.items():
        print(f"\n👉 CATEGORY: {category.upper()}")
        print("-" * 65)
        for i, q in enumerate(queries, 1):
            print(f"[{category} {i}/{len(queries)}] Query: '{q}'")
            try:
                answer, citations = query_rag(q)
                print(f"Response:\n{answer}\n")
            except Exception as e:
                print(f"Error during query: {e}\n")
                
    print("=" * 65)
    print("TEST COMPLETE")
    print("=" * 65)

if __name__ == "__main__":
    run_stress_tests()
