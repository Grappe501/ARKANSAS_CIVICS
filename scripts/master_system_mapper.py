from pathlib import Path
import json
import os
from datetime import datetime

ROOT = Path(__file__).resolve().parents[1]

EXPORT_DIR = ROOT / "exports" / "system_map"
EXPORT_DIR.mkdir(parents=True, exist_ok=True)

ENGINE_DIR = ROOT / "engine"
SCRIPTS_DIR = ROOT / "scripts"
DASHBOARD_DIR = ROOT / "apps" / "editor-dashboard"
COURSES_DIR = ROOT / "content" / "courses"


def build_tree():

    lines = []

    for root, dirs, files in os.walk(ROOT):

        level = root.replace(str(ROOT), "").count(os.sep)
        indent = " " * 2 * level

        folder = Path(root).name
        lines.append(f"{indent}{folder}/")

        subindent = " " * 2 * (level + 1)

        for f in files:
            lines.append(f"{subindent}{f}")

    tree_path = EXPORT_DIR / "project_tree.txt"
    tree_path.write_text("\n".join(lines), encoding="utf-8")

    return tree_path


def inventory_engines():

    engines = []

    if ENGINE_DIR.exists():
        for file in ENGINE_DIR.glob("*.py"):
            engines.append(file.name)

    path = EXPORT_DIR / "engine_inventory.json"
    path.write_text(json.dumps(engines, indent=2))

    return engines


def inventory_scripts():

    scripts = []

    if SCRIPTS_DIR.exists():
        for file in SCRIPTS_DIR.glob("*.py"):
            scripts.append(file.name)

    path = EXPORT_DIR / "script_inventory.json"
    path.write_text(json.dumps(scripts, indent=2))

    return scripts


def inventory_dashboard():

    dashboard_files = []

    if DASHBOARD_DIR.exists():
        for file in DASHBOARD_DIR.glob("*"):
            dashboard_files.append(file.name)

    path = EXPORT_DIR / "dashboard_inventory.json"
    path.write_text(json.dumps(dashboard_files, indent=2))

    return dashboard_files


def inventory_courses():

    course_map = {}

    if COURSES_DIR.exists():

        for course in COURSES_DIR.glob("course_*"):

            chapters = []

            for chapter in course.glob("chapter_*"):

                segments = []

                seg_dir = chapter / "segments"

                if seg_dir.exists():

                    for seg in seg_dir.glob("*.md"):
                        segments.append(seg.name)

                chapters.append({
                    "chapter": chapter.name,
                    "segments": segments
                })

            course_map[course.name] = chapters

    path = EXPORT_DIR / "course_inventory.json"
    path.write_text(json.dumps(course_map, indent=2))

    return course_map


def generate_architecture_report(engines, scripts, dashboard, courses):

    report = []

    report.append("# Arkansas Civics Platform Architecture")
    report.append("")
    report.append(f"Generated: {datetime.utcnow().isoformat()} UTC")
    report.append("")

    report.append("## Engine Modules")
    report.append("")
    for e in engines:
        report.append(f"- {e}")

    report.append("")
    report.append("## Script Modules")
    report.append("")
    for s in scripts:
        report.append(f"- {s}")

    report.append("")
    report.append("## Dashboard Components")
    report.append("")
    for d in dashboard:
        report.append(f"- {d}")

    report.append("")
    report.append("## Courses")
    report.append("")

    for course, chapters in courses.items():

        report.append(f"### {course}")

        for c in chapters:
            report.append(f"- {c['chapter']} ({len(c['segments'])} segments)")

    report_path = EXPORT_DIR / "architecture_report.md"
    report_path.write_text("\n".join(report), encoding="utf-8")

    return report_path


def main():

    print("\nMapping Arkansas Civics Platform...\n")

    tree = build_tree()

    engines = inventory_engines()

    scripts = inventory_scripts()

    dashboard = inventory_dashboard()

    courses = inventory_courses()

    report = generate_architecture_report(
        engines,
        scripts,
        dashboard,
        courses
    )

    print("\nSystem mapping complete.\n")

    print("Outputs:\n")
    print(tree)
    print(report)
    print(EXPORT_DIR / "engine_inventory.json")
    print(EXPORT_DIR / "script_inventory.json")
    print(EXPORT_DIR / "dashboard_inventory.json")
    print(EXPORT_DIR / "course_inventory.json")


if __name__ == "__main__":
    main()