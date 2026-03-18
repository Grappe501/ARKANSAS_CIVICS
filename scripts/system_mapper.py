from pathlib import Path
import json
from collections import defaultdict

ROOT = Path(__file__).resolve().parents[1]

OUTPUT = ROOT / "exports" / "system_map"
OUTPUT.mkdir(parents=True, exist_ok=True)

IGNORE = {
    ".git",
    "__pycache__",
    ".netlify",
    "node_modules",
    ".venv",
    "archive"
}


def skip(path):
    return any(p in IGNORE for p in path.parts)


def map_scripts():

    scripts = []
    scripts_dir = ROOT / "scripts"

    for file in scripts_dir.glob("*.py"):

        scripts.append({
            "name": file.name,
            "path": str(file.relative_to(ROOT)),
            "size": file.stat().st_size
        })

    return scripts


def map_engine():

    engine_files = []

    engine_dir = ROOT / "engine"

    if engine_dir.exists():

        for file in engine_dir.glob("*.py"):

            engine_files.append({
                "name": file.name,
                "path": str(file.relative_to(ROOT))
            })

    return engine_files


def map_content():

    content_counts = defaultdict(int)

    content_dir = ROOT / "content"

    for file in content_dir.rglob("*"):

        if skip(file):
            continue

        if file.is_file():

            ext = file.suffix.lower()
            content_counts[ext] += 1

    return dict(content_counts)


def map_exports():

    exports = []

    exports_dir = ROOT / "exports"

    for folder in exports_dir.iterdir():

        if folder.is_dir():

            exports.append(folder.name)

    return exports


def map_dashboard():

    dashboard_dir = ROOT / "apps/editor-dashboard"

    files = []

    if dashboard_dir.exists():

        for file in dashboard_dir.rglob("*"):

            if file.is_file():

                files.append(str(file.relative_to(ROOT)))

    return files


def build_architecture():

    architecture = {
        "project_root": str(ROOT),
        "layers": {
            "content": map_content(),
            "engine": map_engine(),
            "scripts": map_scripts(),
            "exports": map_exports(),
            "dashboard": map_dashboard()
        }
    }

    return architecture


def build_markdown_map(arch):

    md = []

    md.append("# Arkansas Civics Platform — System Architecture\n")

    md.append("## Content Library\n")

    for ext, count in arch["layers"]["content"].items():
        md.append(f"- {ext}: {count} files")

    md.append("\n## Engine Modules\n")

    for e in arch["layers"]["engine"]:
        md.append(f"- {e['path']}")

    md.append("\n## Build Scripts\n")

    for s in arch["layers"]["scripts"]:
        md.append(f"- {s['path']}")

    md.append("\n## Export Targets\n")

    for e in arch["layers"]["exports"]:
        md.append(f"- exports/{e}")

    md.append("\n## Dashboard Files\n")

    for d in arch["layers"]["dashboard"][:20]:
        md.append(f"- {d}")

    if len(arch["layers"]["dashboard"]) > 20:
        md.append(f"... ({len(arch['layers']['dashboard'])} total files)")

    return "\n".join(md)


def main():

    arch = build_architecture()

    json_file = OUTPUT / "system_architecture.json"
    md_file = OUTPUT / "system_architecture.md"

    json_file.write_text(json.dumps(arch, indent=2), encoding="utf-8")

    md_map = build_markdown_map(arch)
    md_file.write_text(md_map, encoding="utf-8")

    print("\n====================================")
    print(" Arkansas Civics System Map Generated")
    print("====================================\n")

    print("Outputs:\n")

    print(json_file)
    print(md_file)

    print("\nUse this file to understand the platform structure.\n")


if __name__ == "__main__":
    main()