from pathlib import Path
import json
from collections import defaultdict

ROOT = Path(__file__).resolve().parents[1]

OUTPUT_DIR = ROOT / "exports" / "repo_audit"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

IGNORE = {
    ".git",
    "__pycache__",
    ".netlify",
    "node_modules",
    ".venv",
}

TEXT_EXT = {
    ".py", ".md", ".json", ".yaml", ".yml", ".html", ".css",
    ".js", ".txt", ".sql", ".toml"
}


# ------------------------------------------------
# Utility helpers
# ------------------------------------------------

def skip(path: Path) -> bool:
    return any(part in IGNORE for part in path.parts)


def analyze_file(p: Path) -> dict:

    info = {
        "path": str(p.relative_to(ROOT)),
        "suffix": p.suffix.lower(),
        "size_bytes": p.stat().st_size,
    }

    try:
        if p.suffix.lower() in TEXT_EXT:
            text = p.read_text(encoding="utf-8", errors="ignore")
            info["line_count"] = len(text.splitlines())
        else:
            info["line_count"] = None
    except Exception:
        info["line_count"] = None

    return info


def build_tree(dir_path: Path, prefix: str = ""):

    lines = []

    children = sorted(
        [p for p in dir_path.iterdir() if not skip(p)],
        key=lambda p: (p.is_file(), p.name.lower())
    )

    for i, child in enumerate(children):

        connector = "└── " if i == len(children) - 1 else "├── "
        lines.append(prefix + connector + child.name)

        if child.is_dir():

            extension = "    " if i == len(children) - 1 else "│   "
            lines.extend(build_tree(child, prefix + extension))

    return lines


# ------------------------------------------------
# Main audit
# ------------------------------------------------

def main():

    all_files = []
    ext_map = defaultdict(int)
    folder_map = defaultdict(int)

    size_map = defaultdict(int)

    python_scripts = []
    possible_duplicates = defaultdict(list)

    for path in ROOT.rglob("*"):

        if skip(path):
            continue

        if path.is_file():

            info = analyze_file(path)
            all_files.append(info)

            ext_map[info["suffix"]] += 1

            top = Path(info["path"]).parts[0]
            folder_map[top] += 1

            size_map[top] += info["size_bytes"]

            # script tracking
            if info["suffix"] == ".py":
                python_scripts.append(info["path"])

            # duplicate detection by filename
            possible_duplicates[path.name].append(info["path"])

    # ------------------------------------------------
    # Largest folders
    # ------------------------------------------------

    largest_folders = sorted(
        size_map.items(),
        key=lambda x: x[1],
        reverse=True
    )

    # ------------------------------------------------
    # Largest files
    # ------------------------------------------------

    largest_files = sorted(
        all_files,
        key=lambda x: x["size_bytes"],
        reverse=True
    )[:25]

    # ------------------------------------------------
    # Duplicate filenames
    # ------------------------------------------------

    duplicates = {
        name: paths
        for name, paths in possible_duplicates.items()
        if len(paths) > 1
    }

    # ------------------------------------------------
    # Tree structure
    # ------------------------------------------------

    tree = ["ARKANSAS_CIVICS"]
    tree.extend(build_tree(ROOT))

    # ------------------------------------------------
    # Summary
    # ------------------------------------------------

    summary = {
        "root": str(ROOT),
        "total_files": len(all_files),
        "extensions": dict(sorted(ext_map.items())),
        "top_folders": dict(sorted(folder_map.items())),
        "largest_folders_bytes": largest_folders,
        "python_script_count": len(python_scripts),
        "duplicate_filename_count": len(duplicates),
    }

    # ------------------------------------------------
    # Write outputs
    # ------------------------------------------------

    (OUTPUT_DIR / "summary.json").write_text(
        json.dumps(summary, indent=2),
        encoding="utf-8"
    )

    (OUTPUT_DIR / "files.json").write_text(
        json.dumps(all_files, indent=2),
        encoding="utf-8"
    )

    (OUTPUT_DIR / "tree.txt").write_text(
        "\n".join(tree),
        encoding="utf-8"
    )

    (OUTPUT_DIR / "largest_files.json").write_text(
        json.dumps(largest_files, indent=2),
        encoding="utf-8"
    )

    (OUTPUT_DIR / "python_scripts.json").write_text(
        json.dumps(python_scripts, indent=2),
        encoding="utf-8"
    )

    (OUTPUT_DIR / "duplicate_filenames.json").write_text(
        json.dumps(duplicates, indent=2),
        encoding="utf-8"
    )

    print("\n================================================")
    print(" REPOSITORY AUDIT COMPLETE")
    print("================================================\n")

    print("Outputs written to:\n")

    for file in [
        "summary.json",
        "files.json",
        "tree.txt",
        "largest_files.json",
        "python_scripts.json",
        "duplicate_filenames.json"
    ]:
        print(OUTPUT_DIR / file)

    print("\nReady for architectural analysis.\n")


if __name__ == "__main__":
    main()