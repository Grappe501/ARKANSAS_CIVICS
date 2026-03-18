import os

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

PATCH_BLOCK = """import sys
import os

# Add project root to Python path
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

"""

FILES_TO_PATCH = [
    "build_phase_07_graph_persistence.py",
    "load_graph_to_supabase.py",
    "query_civic_graph.py"
]

scripts_dir = os.path.dirname(__file__)

print("\nPhase 07 Import Repair Tool\n")

for file in FILES_TO_PATCH:
    path = os.path.join(scripts_dir, file)

    if not os.path.exists(path):
        print(f"Skipping (not found): {file}")
        continue

    with open(path, "r", encoding="utf-8") as f:
        content = f.read()

    if "PROJECT_ROOT" in content and "sys.path.insert" in content:
        print(f"Already patched: {file}")
        continue

    print(f"Patching: {file}")

    lines = content.splitlines()

    insert_index = 0

    if lines and lines[0].startswith("#!"):
        insert_index = 1

    new_content = (
        "\n".join(lines[:insert_index])
        + "\n"
        + PATCH_BLOCK
        + "\n"
        + "\n".join(lines[insert_index:])
    )

    with open(path, "w", encoding="utf-8") as f:
        f.write(new_content)

print("\nImport patch complete.\n")