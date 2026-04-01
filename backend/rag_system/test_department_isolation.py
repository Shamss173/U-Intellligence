"""
U-Intelligence — Department Isolation Test
File: backend/rag_system/test_department_isolation.py
Run: python test_department_isolation.py
"""

import pickle
import numpy as np
import sys
from pathlib import Path
from collections import defaultdict

# ── Setup ─────────────────────────────────────────────────────────────────────
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from rag_system.rag_pipeline import load_index, retrieve

# ── Define cross-department test cases ────────────────────────────────────────
# Each test: ask a question that belongs to dept A, while filtering for dept B
# Expected result: no relevant chunks should be returned

ISOLATION_TESTS = [

    # HR questions asked in wrong departments
    {
        "query": "What is the maternity leave policy?",
        "correct_dept": "hrg",
        "wrong_dept": "finance",
        "answer_keywords": ["180 days", "maternity leave", "twice in service"]
    },
    {
    "query": "How many annual leave days do employees get?",
    "correct_dept": "hrg",
    "wrong_dept": "finance",
    "answer_keywords": [
        "22 working days",
        "broken period",
        "pro rata basis"
    ]
},
    {
        "query": "What is the probation period for new employees?",
        "correct_dept": "hrg",
        "wrong_dept": "it",
        "answer_keywords": ["probation", "confirmation"]
    },

    # Operations questions asked in wrong departments
    {
        "query": "What is the timeline for CPU to update dishonored cheque report?",
        "correct_dept": "operations_transformation",
        "wrong_dept": "hrg",
        "answer_keywords": ["1:00 PM", "same day", "CBS"]
    },
    {
        "query": "What are the mandatory verification questions for call back?",
        "correct_dept": "operations_transformation",
        "wrong_dept": "it",
        "answer_keywords": ["mother", "favorite city", "mandatory"]
    },

    # IT questions asked in wrong departments
    {
        "query": "What is the IT governance framework?",
        "correct_dept": "it",
        "wrong_dept": "hrg",
        "answer_keywords": ["governance", "IT", "technology"]
    },
    # In test_department_isolation.py — update Test 7:

{
    "query": "What are the data governance policies?",
    "correct_dept": "it",
    "wrong_dept": "operations_transformation",
    "answer_keywords": [
        "IT data governance",
        "data classification",
        "data steward",
        "data quality framework"
    ]
},

    # Finance questions asked in wrong departments
    {
        "query": "What are the financial reporting requirements?",
        "correct_dept": "finance",
        "wrong_dept": "hrg",
        "answer_keywords": ["financial", "reporting"]
    },

    # Treasury questions asked in wrong departments
    {
        "query": "What is the treasury management policy?",
        "correct_dept": "treasury_capital",
        "wrong_dept": "it",
        "answer_keywords": ["treasury", "management"]
    },
    {
        "query": "What are the foreign exchange procedures?",
        "correct_dept": "treasury_capital",
        "wrong_dept": "hrg",
        "answer_keywords": ["foreign exchange", "FX", "currency"]
    },
]

# ── Run Tests ──────────────────────────────────────────────────────────────────
def run_isolation_tests():
    print("=" * 65)
    print("U-INTELLIGENCE — DEPARTMENT ISOLATION TEST")
    print("=" * 65)

    index, metadata_list = load_index()

    passed = 0
    failed = 0
    warnings = 0
    results = []

    for i, test in enumerate(ISOLATION_TESTS):
        query       = test["query"]
        correct     = test["correct_dept"]
        wrong       = test["wrong_dept"]
        keywords    = test["answer_keywords"]

        # ── Test 1: Correct dept should return relevant chunks ─────────────
        correct_chunks = retrieve(
            index, metadata_list, query,
            department_filter=correct
        )

        correct_has_content = len(correct_chunks) > 0
        correct_keyword_hit = False
        if correct_has_content:
            combined_text = " ".join(
                c["text"].lower() for c in correct_chunks[:5]
            )
            correct_keyword_hit = any(
                kw.lower() in combined_text for kw in keywords
            )

        # ── Test 2: Wrong dept should return NO relevant chunks ────────────
        wrong_chunks = retrieve(
            index, metadata_list, query,
            department_filter=wrong
        )

        wrong_has_content = len(wrong_chunks) > 0
        leak_detected = False
        if wrong_has_content:
            combined_wrong = " ".join(
                c["text"].lower() for c in wrong_chunks[:5]
            )
            leak_detected = any(
                kw.lower() in combined_wrong for kw in keywords
            )

        # ── Test 3: Department field check ────────────────────────────────
        wrong_dept_values = set(
            c["metadata"].get("department", "unknown")
            for c in wrong_chunks
        )
        dept_contamination = any(
            d != wrong for d in wrong_dept_values
        )

        # ── Determine result ───────────────────────────────────────────────
        if leak_detected:
            status = "❌ LEAK DETECTED"
            failed += 1
        elif wrong_has_content and not leak_detected:
            status = "⚠️  WRONG DEPT HAS CHUNKS (but no keyword leak)"
            warnings += 1
        else:
            status = "✅ ISOLATED"
            passed += 1

        results.append({
            "test": i + 1,
            "query": query,
            "correct_dept": correct,
            "wrong_dept": wrong,
            "correct_chunks_found": len(correct_chunks),
            "correct_has_keywords": correct_keyword_hit,
            "wrong_chunks_found": len(wrong_chunks),
            "leak_detected": leak_detected,
            "dept_contamination": dept_contamination,
            "status": status
        })

    # ── Print Results ──────────────────────────────────────────────────────────
    print(f"\n{'Test':<5} {'Query':<45} {'Correct Dept':<28} {'Wrong Dept':<28} {'Status'}")
    print("-" * 140)

    for r in results:
        query_short = r["query"][:43] + ".." if len(r["query"]) > 43 else r["query"]
        print(f"  {r['test']:<4} {query_short:<45} {r['correct_dept']:<28} {r['wrong_dept']:<28} {r['status']}")
        print(f"       Correct dept chunks: {r['correct_chunks_found']:>3}  |  "
              f"Keywords found in correct: {'✅' if r['correct_has_keywords'] else '❌'}  |  "
              f"Wrong dept chunks: {r['wrong_chunks_found']:>3}  |  "
              f"Leak: {'❌ YES' if r['leak_detected'] else '✅ NO'}")
        print()

    # ── Summary ────────────────────────────────────────────────────────────────
    total = len(ISOLATION_TESTS)
    isolation_rate = ((passed + warnings) / total) * 100

    print("=" * 65)
    print("ISOLATION TEST SUMMARY")
    print("=" * 65)
    print(f"  Total tests     : {total}")
    print(f"  ✅ Passed        : {passed}")
    print(f"  ⚠️  Warnings      : {warnings}")
    print(f"  ❌ Failed (leaks): {failed}")
    print(f"\n  🎯 Isolation Rate: {isolation_rate:.1f}%")
    print()

    if isolation_rate == 100:
        print("  🚀 PERFECT ISOLATION — No department leakage detected.")
        print("     System is safe for production use.")
    elif isolation_rate >= 90:
        print("  ✅ GOOD ISOLATION — Minor warnings, no critical leaks.")
        print("     Investigate warnings but system is usable.")
    elif isolation_rate >= 70:
        print("  ⚠️  MODERATE ISOLATION — Some leakage detected.")
        print("     Fix leaking departments before production.")
    else:
        print("  ❌ POOR ISOLATION — Significant leakage.")
        print("     Department filtering is not working correctly.")

    print("=" * 65)

    return isolation_rate, results


if __name__ == "__main__":
    rate, results = run_isolation_tests()
