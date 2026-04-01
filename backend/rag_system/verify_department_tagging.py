"""
U-Intelligence — Department Tagging Verification Script
Run this BEFORE full re-embedding to confirm everything is correct.
Place this file in: backend/rag_system/verify_department_tagging.py
Run with: python verify_department_tagging.py
"""

import sqlite3
import sys
from pathlib import Path
from collections import defaultdict

# ── Load metadata ─────────────────────────────────────────────────────────────
METADATA_PATH = Path(__file__).parent / "metadata.db"

print("=" * 60)
print("U-INTELLIGENCE — DEPARTMENT TAGGING VERIFICATION")
print("=" * 60)

if not METADATA_PATH.exists():
    print(f"\n❌ ERROR: metadata.db not found at {METADATA_PATH}")
    print("   Make sure you have run build_index() on your test files first.")
    sys.exit(1)

print(f"\n📂 Loading metadata from: {METADATA_PATH}")

try:
    conn = sqlite3.connect(str(METADATA_PATH))
    conn.row_factory = sqlite3.Row
    rows = conn.execute("SELECT * FROM chunks").fetchall()
    
    # Reconstruct the metadata list of dicts from the database rows
    metadata = []
    for r in rows:
        m = dict(r)
        
        # Ignore soft-deleted chunks
        if m.get("source_file") == "DELETED":
            continue

        # In the DB it is stored as 'department_id', but the pipeline exposes it as 'department' too.
        # We ensure 'department' exists for the checks below.
        if m.get("department_id"):
            m["department"] = m["department_id"]
        metadata.append(m)
        
    conn.close()
except Exception as e:
    print(f"\n❌ ERROR reading database: {e}")
    sys.exit(1)

print(f"✅ Loaded {len(metadata)} total chunks\n")

# ── CHECK 1: department field exists ─────────────────────────────────────────
print("─" * 60)
print("CHECK 1 — Does 'department' field exist in metadata?")
print("─" * 60)

has_department   = sum(1 for m in metadata if "department" in m and m["department"])
missing_dept     = sum(1 for m in metadata if "department" not in m)
empty_dept       = sum(1 for m in metadata if "department" in m and not m["department"])

print(f"  ✅ Chunks WITH department field   : {has_department}")
print(f"  ❌ Chunks WITHOUT department field : {missing_dept}")
print(f"  ⚠️  Chunks with EMPTY department   : {empty_dept}")

if missing_dept > 0 or empty_dept > 0:
    print("\n  ❌ FAIL — Some chunks are missing department tag.")
    print("     Check that build_index() changes were applied correctly.")
else:
    print("\n  ✅ PASS — All chunks have department field.")

# ── CHECK 2: Unique department values ─────────────────────────────────────────
print("\n" + "─" * 60)
print("CHECK 2 — What department values are in metadata?")
print("─" * 60)

dept_counts = defaultdict(int)
for m in metadata:
    dept = m.get("department") or "MISSING"
    dept_counts[dept] += 1

print(f"\n  {'Department Value':<35} {'Chunks':>8}  {'Status'}")
print(f"  {'-'*35} {'-'*8}  {'-'*20}")

EXPECTED_DB_CODES = {
    "hrg", "branch_banking", "compliance", "cibg",
    "digital_banking", "finance", "it", "islamic_banking",
    "legal_secretary", "operations_transformation",
    "risk_credit", "shared_services", "special_assets",
    "treasury_capital", "ubl_international", "consumer_banking"
}

all_pass = True
if not dept_counts:
    print("  No departments found.")
else:
    for dept, count in sorted(dept_counts.items()):
        if dept in EXPECTED_DB_CODES:
            status = "✅ Matches DB code"
        elif dept == "MISSING":
            status = "❌ No department field"
            all_pass = False
        else:
            status = "⚠️  Does NOT match any DB code"
            all_pass = False
        print(f"  {dept:<35} {count:>8}  {status}")

if all_pass and dept_counts:
    print("\n  ✅ PASS — All department values match DB codes exactly.")
else:
    print("\n  ❌ FAIL — Some departments don't match DB codes.")
    print("     Check folder names match DB codes exactly (e.g. 'hrg' not 'HRG')")

# ── CHECK 3: Nested file tagging ──────────────────────────────────────────────
print("\n" + "─" * 60)
print("CHECK 3 — Are nested files tagged with ROOT department?")
print("─" * 60)

nested_issues = []
for m in metadata:
    folder_path  = m.get("folder_path", "")
    department   = m.get("department", "")
    # The immediate parent folder name
    immediate_parent = Path(folder_path).name if folder_path else ""
    
    # If immediate parent != department, it means file was nested
    # and department should still be the root dept code
    if immediate_parent != department:
        if department in EXPECTED_DB_CODES:
            # This is CORRECT — nested file tagged with root dept
            pass
        else:
            nested_issues.append({
                "file":        m.get("source_file", "unknown"),
                "folder_path": folder_path,
                "department":  department,
                "immediate_parent": immediate_parent
            })

if not nested_issues:
    print("  ✅ PASS — All nested files correctly tagged with root department.")
else:
    print(f"  ❌ FAIL — {len(nested_issues)} chunks have incorrect nested tagging:")
    for issue in nested_issues[:5]:  # show first 5
        print(f"\n     File      : {issue['file']}")
        print(f"     folder_path: {issue['folder_path']}")
        print(f"     department : {issue['department']}")
        print(f"     Expected   : one of the 16 DB codes")

# ── CHECK 4: Sample chunk detail ──────────────────────────────────────────────
print("\n" + "─" * 60)
print("CHECK 4 — Sample chunk detail (first 3 chunks)")
print("─" * 60)

for i, m in enumerate(metadata[:3]):
    print(f"\n  Chunk {i}:")
    print(f"    source_file : {m.get('source_file', 'N/A')}")
    print(f"    folder_path : {m.get('folder_path', 'N/A')}")
    print(f"    department  : {m.get('department', '❌ MISSING')}")
    print(f"    chunk_id    : {m.get('chunk_id', 'N/A')}")
    print(f"    page_number : {m.get('page_number', 'N/A')}")
    print(f"    text preview: {str(m.get('text', ''))[:80]}...")

# ── CHECK 5: Filter simulation ────────────────────────────────────────────────
print("\n" + "─" * 60)
print("CHECK 5 — Filter simulation (does filtering return correct chunks?)")
print("─" * 60)

for dept_code in sorted(dept_counts.keys()):
    if dept_code == "MISSING":
        continue
    filtered = [m for m in metadata if m.get("department", "").lower() == dept_code.lower()]
    files_in_dept = set(m.get("source_file", "") for m in filtered)
    print(f"\n  department_filter = '{dept_code}'")
    print(f"    Chunks returned : {len(filtered)}")
    print(f"    Unique files    : {len(files_in_dept)}")
    for f in sorted(files_in_dept):
        print(f"      📄 {f}")

# ── FINAL SUMMARY ─────────────────────────────────────────────────────────────
print("\n" + "=" * 60)
print("FINAL SUMMARY")
print("=" * 60)

checks = {
    "department field exists in all chunks" : missing_dept == 0 and empty_dept == 0,
    "all dept values match DB codes"        : all_pass and bool(dept_counts),
    "nested files tagged correctly"         : len(nested_issues) == 0,
}

all_good = True
for check, passed in checks.items():
    icon = "✅" if passed else "❌"
    print(f"  {icon}  {check}")
    if not passed:
        all_good = False

print()
if all_good:
    print("  🚀 ALL CHECKS PASSED — Safe to run full re-embedding of all 1,139 files!")
else:
    print("  ⛔ ISSUES FOUND — Fix the above before full re-embedding.")
    print("     Full re-embedding with broken tagging = wasted API cost.")

print("=" * 60)
