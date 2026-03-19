from __future__ import annotations

import json
import re
from pathlib import Path
from datetime import datetime, UTC

ROOT = Path(__file__).resolve().parents[1]
CONTENT_DIR = ROOT / "content" / "courses"
MANIFEST_PATH = ROOT / "apps" / "editor-dashboard" / "content-manifest.json"
OUTPUT_DIR = ROOT / "exports" / "dashboard"
JSON_OUT = OUTPUT_DIR / "phase09_content.json"
JS_OUT = OUTPUT_DIR / "phase09_content.js"


def sort_key(value: str):
    parts = re.split(r"(\d+)", str(value).lower())
    return [int(p) if p.isdigit() else p for p in parts]


def safe_title(value: str) -> str:
    text = str(value).replace("_", " ").replace("-", " ").strip()
    return " ".join(word.capitalize() if not word.isupper() else word for word in text.split()) or "Untitled"


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return path.read_text(encoding="latin-1")


def build_from_filesystem() -> dict:
    courses = []
    total_chapters = 0
    total_segments = 0

    for course_dir in sorted([p for p in CONTENT_DIR.iterdir() if p.is_dir()], key=lambda p: sort_key(p.name)):
        chapters = []
        for chapter_dir in sorted([p for p in course_dir.iterdir() if p.is_dir()], key=lambda p: sort_key(p.name)):
            segment_dir = chapter_dir / "segments"
            segment_files = []
            if segment_dir.exists():
                segment_files = sorted(segment_dir.glob("*.md"), key=lambda p: sort_key(p.name))
            else:
                segment_files = sorted(chapter_dir.glob("*.md"), key=lambda p: sort_key(p.name))

            segments = []
            for segment_file in segment_files:
                rel_path = segment_file.relative_to(ROOT).as_posix()
                body = read_text(segment_file)
                lines = body.splitlines()
                preview = " ".join(line.strip() for line in lines[:4] if line.strip())[:220]
                segments.append({
                    "slug": segment_file.stem,
                    "title": safe_title(segment_file.stem),
                    "path": rel_path,
                    "line_count": len(lines),
                    "word_count": len(body.split()),
                    "preview": preview,
                    "content": body,
                })

            chapters.append({
                "slug": chapter_dir.name,
                "title": safe_title(chapter_dir.name),
                "path": chapter_dir.relative_to(ROOT).as_posix(),
                "segment_count": len(segments),
                "segments": segments,
            })
            total_chapters += 1
            total_segments += len(segments)

        courses.append({
            "slug": course_dir.name,
            "title": safe_title(course_dir.name),
            "path": course_dir.relative_to(ROOT).as_posix(),
            "chapter_count": len(chapters),
            "segment_count": sum(c["segment_count"] for c in chapters),
            "chapters": chapters,
        })

    return {
        "generated_at": datetime.now(UTC).isoformat(),
        "source": "filesystem_scan",
        "course_count": len(courses),
        "chapter_count": total_chapters,
        "segment_count": total_segments,
        "courses": courses,
    }


def try_manifest() -> dict | None:
    if not MANIFEST_PATH.exists():
        return None
    try:
        raw = json.loads(read_text(MANIFEST_PATH))
    except Exception:
        return None
    # If it is already normalized, trust it only for metadata. Content still comes from files.
    if isinstance(raw, dict) and isinstance(raw.get("courses"), list):
        return raw
    return None


def enrich_from_manifest(payload: dict, manifest: dict | None) -> dict:
    if not manifest:
        return payload
    names = {str(c.get("slug") or c.get("name")): c.get("name") for c in manifest.get("courses", []) if isinstance(c, dict)}
    for course in payload.get("courses", []):
        course["title"] = names.get(course["slug"], course["title"])
    payload["source"] = "filesystem_scan+manifest_metadata"
    return payload


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    if not CONTENT_DIR.exists():
        raise SystemExit(f"Missing content directory: {CONTENT_DIR}")

    payload = build_from_filesystem()
    payload = enrich_from_manifest(payload, try_manifest())

    JSON_OUT.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    JS_OUT.write_text(
        "window.PHASE09_CONTENT = " + json.dumps(payload, ensure_ascii=False) + ";\n",
        encoding="utf-8",
    )

    print("=" * 48)
    print("PHASE 09 STATIC DASHBOARD BUILD COMPLETE")
    print("=" * 48)
    print(f"Courses:  {payload['course_count']}")
    print(f"Chapters: {payload['chapter_count']}")
    print(f"Segments: {payload['segment_count']}")
    print()
    print("Outputs:")
    print(JSON_OUT)
    print(JS_OUT)


if __name__ == "__main__":
    main()
