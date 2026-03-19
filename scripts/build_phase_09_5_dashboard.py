#!/usr/bin/env python3
"""
Build Phase 09.5 content bundle from real filesystem course data.

Output:
- exports/dashboard/phase095_content.json
- exports/dashboard/phase095_content.js
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Dict, List, Tuple


ROOT = Path(__file__).resolve().parents[1]
COURSES_DIR = ROOT / "content" / "courses"
EXPORT_DIR = ROOT / "exports" / "dashboard"
EXPORT_DIR.mkdir(parents=True, exist_ok=True)

FRONTMATTER_RE = re.compile(r"^---\n(.*?)\n---\n(.*)$", re.DOTALL)
LIST_ITEM_RE = re.compile(r"^\s*-\s+(.*)$")


def prettify_slug(slug: str) -> str:
    text = slug.replace("_", " ").replace("-", " ").strip()
    text = re.sub(r"^\d+\s+", "", text)
    return " ".join(word.capitalize() for word in text.split())


def parse_loose_yaml(text: str) -> Dict:
    """
    Tolerant parser for the malformed course.yaml files in this repo.
    Only extracts simple key: value pairs and top-level lists.
    """
    result: Dict = {}
    current_key = None

    for raw in text.splitlines():
        line = raw.strip()
        if not line:
            continue

        list_match = LIST_ITEM_RE.match(line)
        if list_match and current_key:
            result.setdefault(current_key, [])
            result[current_key].append(list_match.group(1).strip())
            continue

        if ":" in line:
            key, value = line.split(":", 1)
            key = key.strip()
            value = value.strip()

            if not value:
                result[key] = []
                current_key = key
                continue

            # strip quotes
            if (value.startswith('"') and value.endswith('"')) or (value.startswith("'") and value.endswith("'")):
                value = value[1:-1]

            # primitive coercion
            if value.lower() in {"true", "false"}:
                parsed_value = value.lower() == "true"
            else:
                try:
                    parsed_value = int(value)
                except ValueError:
                    parsed_value = value

            result[key] = parsed_value
            current_key = key
    return result


def parse_markdown_segment(path: Path) -> Dict:
    text = path.read_text(encoding="utf-8")
    meta = {}
    body = text

    m = FRONTMATTER_RE.match(text)
    if m:
        front, body = m.groups()
        lines = front.splitlines()
        current_list_key = None
        for raw in lines:
            line = raw.rstrip()
            if not line.strip():
                continue
            list_match = LIST_ITEM_RE.match(line.strip())
            if list_match and current_list_key:
                meta.setdefault(current_list_key, [])
                meta[current_list_key].append(list_match.group(1).strip())
                continue
            if ":" in line:
                key, value = line.split(":", 1)
                key = key.strip()
                value = value.strip()
                if not value:
                    meta[key] = []
                    current_list_key = key
                else:
                    if (value.startswith('"') and value.endswith('"')) or (value.startswith("'") and value.endswith("'")):
                        value = value[1:-1]
                    meta[key] = value
                    current_list_key = key

    lines = [ln.strip() for ln in body.splitlines() if ln.strip()]
    title = meta.get("title")
    if not title:
        for ln in lines:
            if ln.startswith("# "):
                title = ln[2:].strip()
                break
    title = title or prettify_slug(path.stem)

    content = body.strip()
    preview = re.sub(r"\s+", " ", content)[:180]
    word_count = len(re.findall(r"\b\w+\b", content))

    return {
        "slug": path.stem,
        "title": title,
        "path": str(path.relative_to(ROOT)).replace("\\", "/"),
        "tags": meta.get("tags", []),
        "content": content,
        "preview": preview,
        "word_count": word_count,
    }


def chapter_sort_key(name: str) -> Tuple[int, str]:
    m = re.match(r"chapter_(\d+)", name)
    return (int(m.group(1)) if m else 9999, name)


def build_course(course_dir: Path) -> Dict:
    course_meta = {}
    course_yaml = course_dir / "course.yaml"
    if course_yaml.exists():
        course_meta = parse_loose_yaml(course_yaml.read_text(encoding="utf-8"))

    # Prefer chapter list from course.yaml if present
    chapter_names = list(course_meta.get("chapters", [])) if isinstance(course_meta.get("chapters"), list) else []

    # Fallback to descriptive chapter_* folders with chapter.yaml
    if not chapter_names:
        chapter_names = [
            p.name for p in sorted(course_dir.glob("chapter_*"), key=lambda p: chapter_sort_key(p.name))
            if p.is_dir() and (p / "chapter.yaml").exists()
        ]

    # Final fallback to any chapter_* folder that has segments
    if not chapter_names:
        chapter_names = [
            p.name for p in sorted(course_dir.glob("chapter_*"), key=lambda p: chapter_sort_key(p.name))
            if p.is_dir() and (p / "segments").exists()
        ]

    chapters = []
    for chapter_name in chapter_names:
        chapter_dir = course_dir / chapter_name
        if not chapter_dir.exists():
            continue

        chapter_meta = {}
        chapter_yaml = chapter_dir / "chapter.yaml"
        if chapter_yaml.exists():
            chapter_meta = parse_loose_yaml(chapter_yaml.read_text(encoding="utf-8"))

        segment_dir = chapter_dir / "segments"
        segment_paths = sorted(segment_dir.glob("*.md")) if segment_dir.exists() else []
        segments = [parse_markdown_segment(path) for path in segment_paths]

        chapters.append({
            "slug": chapter_name,
            "title": chapter_meta.get("title", prettify_slug(chapter_name)),
            "path": str(chapter_dir.relative_to(ROOT)).replace("\\", "/"),
            "segment_count": len(segments),
            "segments": segments,
        })

    title = course_meta.get("title", prettify_slug(course_dir.name))
    total_segments = sum(ch["segment_count"] for ch in chapters)

    return {
        "slug": course_dir.name,
        "title": title,
        "path": str(course_dir.relative_to(ROOT)).replace("\\", "/"),
        "chapter_count": len(chapters),
        "segment_count": total_segments,
        "theme": course_meta.get("theme", ""),
        "chapters": chapters,
    }


def main() -> None:
    if not COURSES_DIR.exists():
        raise SystemExit(f"Courses directory not found: {COURSES_DIR}")

    course_dirs = [p for p in sorted(COURSES_DIR.iterdir()) if p.is_dir() and p.name.startswith("course_")]
    courses = [build_course(course_dir) for course_dir in course_dirs]

    payload = {
        "generated_at": __import__("datetime").datetime.now(__import__("datetime").UTC).isoformat(),
        "source": "filesystem_real_course_scan",
        "course_count": len(courses),
        "chapter_count": sum(c["chapter_count"] for c in courses),
        "segment_count": sum(c["segment_count"] for c in courses),
        "courses": courses,
    }

    json_path = EXPORT_DIR / "phase095_content.json"
    js_path = EXPORT_DIR / "phase095_content.js"

    json_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    js_path.write_text("window.PHASE095_CONTENT = " + json.dumps(payload, ensure_ascii=False) + ";", encoding="utf-8")

    print("\\n=== PHASE 09.5 CONTENT BUILD COMPLETE ===")
    print(f"Courses:  {payload['course_count']}")
    print(f"Chapters: {payload['chapter_count']}")
    print(f"Segments: {payload['segment_count']}")
    print(f"JSON:     {json_path}")
    print(f"JS:       {js_path}")


if __name__ == "__main__":
    main()
