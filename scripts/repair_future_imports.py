import os

scripts_dir = os.path.dirname(__file__)

FILES = [
    "build_phase_07_graph_persistence.py",
    "load_graph_to_supabase.py",
    "query_civic_graph.py"
]

PATCH = """
import sys
import os

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)
"""

print("\nRepairing __future__ import placement...\n")

for file in FILES:
    path = os.path.join(scripts_dir, file)

    if not os.path.exists(path):
        print(f"Missing: {file}")
        continue

    with open(path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    future_index = None

    for i, line in enumerate(lines):
        if "from __future__ import" in line:
            future_index = i
            break

    # Remove any existing PROJECT_ROOT patch
    cleaned = []
    skip = False

    for line in lines:
        if "PROJECT_ROOT =" in line:
            skip = True
        if not skip:
            cleaned.append(line)
        if skip and line.strip() == "":
            skip = False

    if future_index is None:
        insert_at = 0
    else:
        insert_at = future_index + 1

    cleaned.insert(insert_at, PATCH + "\n")

    with open(path, "w", encoding="utf-8") as f:
        f.writelines(cleaned)

    print(f"Repaired: {file}")

print("\nAll scripts repaired.\n")