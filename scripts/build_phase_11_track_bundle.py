#!/usr/bin/env python3
"""
Build Phase 11 content bundle from real filesystem course data.

Outputs:
- exports/dashboard/phase11_content.json
- exports/dashboard/phase11_content.js
"""
from __future__ import annotations

import json
import re
from datetime import datetime, UTC
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
            if (value.startswith('"') and value.endswith('"')) or (value.startswith("'") and value.endswith("'")):
                value = value[1:-1]
            if value.lower() in {"true", "false"}:
                parsed = value.lower() == "true"
            else:
                try:
                    parsed = int(value)
                except ValueError:
                    parsed = value
            result[key] = parsed
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
    preview = re.sub(r"\s+", " ", content)[:220]
    word_count = len(re.findall(r"\b\w+\b", content))
    tags = meta.get("tags", [])
    if isinstance(tags, str):
        tags = [tags]

    return {
        "slug": path.stem,
        "title": title,
        "path": str(path.relative_to(ROOT)).replace("\\", "/"),
        "tags": tags,
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

    chapter_names = list(course_meta.get("chapters", [])) if isinstance(course_meta.get("chapters"), list) else []
    if not chapter_names:
        chapter_names = [
            p.name for p in sorted(course_dir.glob("chapter_*"), key=lambda p: chapter_sort_key(p.name))
            if p.is_dir() and ((p / "chapter.yaml").exists() or (p / "segments").exists())
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

def build_roles(courses: List[Dict]) -> List[Dict]:
    course_slugs = [c["slug"] for c in courses]
    def existing(*preferred):
        return [slug for slug in preferred if slug in course_slugs][:3] or course_slugs[:3]

    return [
        {
            "id": "community_member",
            "title": "Community Member",
            "description": "Build civic confidence, local awareness, and a practical understanding of how power works nearby.",
            "priority_courses": existing("course_01_civic_awakening", "course_02_local_government", "course_03_public_process"),
            "priority_tags": ["local", "community", "participation", "government"],
            "gates": [
                {"title": "Role Activated", "description": "Choose a role to activate guided recommendations.", "target_course": existing("course_01_civic_awakening")[0] if existing("course_01_civic_awakening") else "", "requires_role": True, "min_completed": 0},
                {"title": "Foundation Gate", "description": "Complete 5 lessons to unlock broader civic study.", "target_course": existing("course_02_local_government")[0] if len(existing("course_02_local_government")) else "", "requires_role": True, "min_completed": 5},
                {"title": "Advanced Awareness Gate", "description": "Complete 15 lessons to unlock more advanced paths.", "target_course": existing("course_03_public_process")[0] if len(existing("course_03_public_process")) else "", "requires_role": True, "min_completed": 15},
            ],
        },
        {
            "id": "volunteer",
            "title": "Volunteer",
            "description": "Train for reliable movement participation, outreach discipline, and practical teamwork.",
            "priority_courses": existing("course_01_civic_awakening", "course_04_campaign_basics", "course_05_volunteer_coordination"),
            "priority_tags": ["action", "team", "volunteer", "outreach", "organizing"],
            "gates": [
                {"title": "Volunteer Start", "description": "Choose the volunteer role to unlock the starter queue.", "target_course": existing("course_04_campaign_basics")[0] if existing("course_04_campaign_basics") else "", "requires_role": True, "min_completed": 0},
                {"title": "Field Readiness", "description": "Complete 8 lessons to unlock broader campaign-support work.", "target_course": existing("course_05_volunteer_coordination")[0] if existing("course_05_volunteer_coordination") else "", "requires_role": True, "min_completed": 8},
            ],
        },
        {
            "id": "organizer",
            "title": "Organizer",
            "description": "Focus on strategy, community power, leadership, escalation, and disciplined collective action.",
            "priority_courses": existing("course_01_civic_awakening", "course_06_organizing", "course_07_strategy"),
            "priority_tags": ["strategy", "organizing", "power", "leadership", "community"],
            "gates": [
                {"title": "Organizer Foundation", "description": "Choose the organizer role to unlock your path.", "target_course": existing("course_06_organizing")[0] if existing("course_06_organizing") else "", "requires_role": True, "min_completed": 0},
                {"title": "Leadership Gate", "description": "Complete 12 lessons to unlock higher strategy work.", "target_course": existing("course_07_strategy")[0] if existing("course_07_strategy") else "", "requires_role": True, "min_completed": 12},
                {"title": "Movement Gate", "description": "Complete 30 lessons to unlock advanced movement-building content.", "target_course": existing("course_08_leadership")[0] if "course_08_leadership" in course_slugs else existing()[0], "requires_role": True, "min_completed": 30},
            ],
        },
        {
            "id": "researcher",
            "title": "Researcher",
            "description": "Develop evidence skills, documentation habits, institutional memory, and issue depth.",
            "priority_courses": existing("course_01_civic_awakening", "course_09_research", "course_10_policy_analysis"),
            "priority_tags": ["research", "evidence", "policy", "analysis", "history"],
            "gates": [
                {"title": "Research Start", "description": "Choose the researcher role to unlock guided study.", "target_course": existing("course_09_research")[0] if existing("course_09_research") else "", "requires_role": True, "min_completed": 0},
                {"title": "Policy Depth", "description": "Complete 10 lessons to unlock advanced policy analysis.", "target_course": existing("course_10_policy_analysis")[0] if existing("course_10_policy_analysis") else "", "requires_role": True, "min_completed": 10},
            ],
        },
        {
            "id": "media_radio",
            "title": "Media / Radio",
            "description": "Learn public narrative, audience development, message discipline, and movement communication.",
            "priority_courses": existing("course_01_civic_awakening", "course_11_media", "course_12_storytelling"),
            "priority_tags": ["media", "story", "narrative", "radio", "audience", "message"],
            "gates": [
                {"title": "Media Start", "description": "Choose the media role to unlock a communication-focused path.", "target_course": existing("course_11_media")[0] if existing("course_11_media") else "", "requires_role": True, "min_completed": 0},
                {"title": "Narrative Depth", "description": "Complete 8 lessons to unlock deeper message work.", "target_course": existing("course_12_storytelling")[0] if existing("course_12_storytelling") else "", "requires_role": True, "min_completed": 8},
            ],
        },
    ]

def main() -> None:
    if not COURSES_DIR.exists():
        raise SystemExit(f"Courses directory not found: {COURSES_DIR}")

    course_dirs = [p for p in sorted(COURSES_DIR.iterdir()) if p.is_dir() and p.name.startswith("course_")]
    courses = [build_course(course_dir) for course_dir in course_dirs]

    payload = {
        "generated_at": datetime.now(UTC).isoformat(),
        "source": "filesystem_real_course_scan_phase11",
        "course_count": len(courses),
        "chapter_count": sum(c["chapter_count"] for c in courses),
        "segment_count": sum(c["segment_count"] for c in courses),
        "roles": build_roles(courses),
        "courses": courses,
    }

    json_path = EXPORT_DIR / "phase11_content.json"
    js_path = EXPORT_DIR / "phase11_content.js"
    json_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    js_path.write_text("window.PHASE11_CONTENT = " + json.dumps(payload, ensure_ascii=False) + ";", encoding="utf-8")

    print("\\n=== PHASE 11 FULL TRACK BUNDLE COMPLETE ===")
    print(f"Courses:  {payload['course_count']}")
    print(f"Chapters: {payload['chapter_count']}")
    print(f"Segments: {payload['segment_count']}")
    print(f"Roles:    {len(payload['roles'])}")
    print(f"JSON:     {json_path}")
    print(f"JS:       {js_path}")

if __name__ == "__main__":
    main()
