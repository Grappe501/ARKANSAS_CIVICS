from pathlib import Path
import shutil
import json

ROOT = Path(__file__).resolve().parents[1]
CONTENT_SRC = ROOT / "content" / "courses"
DASHBOARD_CONTENT = ROOT / "apps" / "editor-dashboard" / "content"

def main():
    if DASHBOARD_CONTENT.exists():
        shutil.rmtree(DASHBOARD_CONTENT)

    DASHBOARD_CONTENT.mkdir(parents=True, exist_ok=True)

    manifest = {}

    for course in sorted(CONTENT_SRC.glob("course_*")):
        course_out = DASHBOARD_CONTENT / course.name
        course_out.mkdir(parents=True, exist_ok=True)
        manifest[course.name] = {}

        for chapter in sorted(course.glob("chapter_*")):
            chapter_out = course_out / chapter.name
            chapter_out.mkdir(parents=True, exist_ok=True)

            seg_out = chapter_out / "segments"
            seg_out.mkdir(parents=True, exist_ok=True)

            manifest[course.name][chapter.name] = []

            src_seg_dir = chapter / "segments"
            if not src_seg_dir.exists():
                continue

            for seg in sorted(src_seg_dir.glob("*.md")):
                dst = seg_out / seg.name
                shutil.copy2(seg, dst)
                manifest[course.name][chapter.name].append(f"segments/{seg.name}")

    manifest_path = ROOT / "apps" / "editor-dashboard" / "content-manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")

    print("\nDashboard content copied.")
    print(f"Manifest written to: {manifest_path}")
    print(f"Content copied to: {DASHBOARD_CONTENT}")

if __name__ == "__main__":
    main()
