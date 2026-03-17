from pathlib import Path
import json
from collections import defaultdict

ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR = ROOT / "exports" / "project_map"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

IGNORE_DIRS = {
    "__pycache__",
    ".git",
    ".netlify",
    "node_modules",
}

TEXT_EXTENSIONS = {
    ".py", ".md", ".json", ".yaml", ".yml", ".html", ".css", ".js", ".toml", ".sql", ".txt"
}


def should_skip(path: Path) -> bool:
    return any(part in IGNORE_DIRS for part in path.parts)


def file_info(path: Path) -> dict:
    info = {
        "path": str(path.relative_to(ROOT)),
        "name": path.name,
        "suffix": path.suffix.lower(),
        "size_bytes": path.stat().st_size,
    }

    try:
        if path.suffix.lower() in TEXT_EXTENSIONS:
            text = path.read_text(encoding="utf-8", errors="ignore")
            info["line_count"] = len(text.splitlines())
            info["char_count"] = len(text)
        else:
            info["line_count"] = None
            info["char_count"] = None
    except Exception:
        info["line_count"] = None
        info["char_count"] = None

    return info


def build_tree(path: Path, prefix: str = "") -> list[str]:
    lines = []
    children = sorted(
        [p for p in path.iterdir() if not should_skip(p)],
        key=lambda p: (p.is_file(), p.name.lower())
    )

    for i, child in enumerate(children):
        connector = "└── " if i == len(children) - 1 else "├── "
        lines.append(f"{prefix}{connector}{child.name}")
        if child.is_dir():
            extension = "    " if i == len(children) - 1 else "│   "
            lines.extend(build_tree(child, prefix + extension))
    return lines


def main():
    all_files = []
    by_extension = defaultdict(list)
    by_top_folder = defaultdict(list)

    for path in ROOT.rglob("*"):
        if should_skip(path):
            continue
        if path.is_file():
            info = file_info(path)
            all_files.append(info)
            by_extension[info["suffix"]].append(info["path"])

            parts = Path(info["path"]).parts
            top = parts[0] if parts else "."
            by_top_folder[top].append(info["path"])

    tree_lines = [ROOT.name]
    tree_lines.extend(build_tree(ROOT))

    summary = {
        "root": str(ROOT),
        "file_count": len(all_files),
        "top_level_folders": sorted(by_top_folder.keys()),
        "extensions": {k: len(v) for k, v in sorted(by_extension.items())},
    }

    (OUTPUT_DIR / "project_tree.txt").write_text("\n".join(tree_lines), encoding="utf-8")
    (OUTPUT_DIR / "project_files.json").write_text(json.dumps(all_files, indent=2), encoding="utf-8")
    (OUTPUT_DIR / "project_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")

    top_folder_report = []
    for folder, files in sorted(by_top_folder.items()):
        top_folder_report.append(f"# {folder}")
        top_folder_report.append(f"Count: {len(files)}")
        top_folder_report.append("")
        for file in sorted(files):
            top_folder_report.append(f"- {file}")
        top_folder_report.append("")

    (OUTPUT_DIR / "top_folder_report.md").write_text("\n".join(top_folder_report), encoding="utf-8")

    print("\nProject mapping complete.\n")
    print(f"Tree: {OUTPUT_DIR / 'project_tree.txt'}")
    print(f"Files: {OUTPUT_DIR / 'project_files.json'}")
    print(f"Summary: {OUTPUT_DIR / 'project_summary.json'}")
    print(f"Folder report: {OUTPUT_DIR / 'top_folder_report.md'}")
    print("")


if __name__ == "__main__":
    main()