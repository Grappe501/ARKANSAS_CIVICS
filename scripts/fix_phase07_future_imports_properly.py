import os

scripts_dir = os.path.dirname(__file__)

FILES = [
    "build_phase_07_graph_persistence.py",
    "load_graph_to_supabase.py",
    "query_civic_graph.py"
]

PATCH = [
    "import sys\n",
    "import os\n",
    "\n",
    "# Add project root to Python path\n",
    "PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))\n",
    "if PROJECT_ROOT not in sys.path:\n",
    "    sys.path.insert(0, PROJECT_ROOT)\n",
    "\n"
]

print("\nFixing __future__ import placement properly...\n")

for file in FILES:
    path = os.path.join(scripts_dir, file)

    if not os.path.exists(path):
        print(f"Missing: {file}")
        continue

    with open(path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    future_line = None
    cleaned_lines = []

    # Find the future import
    for line in lines:
        if line.strip().startswith("from __future__ import"):
            future_line = line
        else:
            # remove previous path patches if present
            if "PROJECT_ROOT" in line or "sys.path.insert" in line:
                continue
            cleaned_lines.append(line)

    if future_line is None:
        print(f"No future import found in {file}, skipping.")
        continue

    # Rebuild file structure
    new_content = []
    new_content.append(future_line)
    new_content.extend(PATCH)
    new_content.extend(cleaned_lines)

    with open(path, "w", encoding="utf-8") as f:
        f.writelines(new_content)

    print(f"Fixed: {file}")

print("\nAll Phase 07 scripts corrected.\n")