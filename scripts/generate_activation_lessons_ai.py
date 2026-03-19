#!/usr/bin/env python3
"""
Phase 13 — AI Auto-Generation for Activation Lessons

Modes:
- template: deterministic transformation from source lesson text
- openai: uses OpenAI API if OPENAI_API_KEY is set and openai package is installed

Examples:
python scripts/generate_activation_lessons_ai.py --course course_01_civic_awakening --chapter chapter_01 --mode template
python scripts/generate_activation_lessons_ai.py --course course_01_civic_awakening --chapter chapter_01 --mode openai
python scripts/generate_activation_lessons_ai.py --all --mode template
"""

from __future__ import annotations

import argparse
import json
import os
import re
from dataclasses import dataclass, asdict
from datetime import datetime, UTC
from pathlib import Path
from typing import Dict, List, Optional

ROOT = Path(__file__).resolve().parents[1]
COURSES_DIR = ROOT / "content" / "courses"
OUTPUT_DIR = ROOT / "exports" / "activation_generated"
PROMPT_PATH = ROOT / "prompts" / "activation_lesson_prompt.txt"
CONFIG_PATH = ROOT / "config" / "phase13_generation_config.json"

FRONTMATTER_RE = re.compile(r"^---\n(.*?)\n---\n(.*)$", re.DOTALL)
LIST_ITEM_RE = re.compile(r"^\s*-\s+(.*)$")


@dataclass
class ActivationLesson:
    source_path: str
    course_slug: str
    chapter_slug: str
    segment_slug: str
    title: str
    hook: str
    reality: str
    actions: List[str]
    reflection: str
    next_step: str
    tags: List[str]
    generated_by: str


def load_config() -> Dict:
    if CONFIG_PATH.exists():
        return json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    return {
        "default_neutral_tone": True,
        "default_action_count": 3,
        "organization_name": "Stand Up Arkansas",
        "audience": "Arkansas civic learners",
    }


def prettify_slug(slug: str) -> str:
    text = slug.replace("_", " ").replace("-", " ").strip()
    text = re.sub(r"^\d+\s+", "", text)
    return " ".join(word.capitalize() for word in text.split())


def parse_frontmatter(text: str) -> tuple[Dict, str]:
    meta = {}
    body = text
    m = FRONTMATTER_RE.match(text)
    if m:
        front, body = m.groups()
        current_list_key = None
        for raw in front.splitlines():
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
    return meta, body.strip()


def extract_title(meta: Dict, body: str, fallback_slug: str) -> str:
    title = meta.get("title")
    if title:
        return title
    for line in body.splitlines():
        line = line.strip()
        if line.startswith("# "):
            return line[2:].strip()
    return prettify_slug(fallback_slug)


def summarize_text(text: str, limit: int = 300) -> str:
    cleaned = re.sub(r"\s+", " ", text).strip()
    return cleaned[:limit].rstrip() + ("..." if len(cleaned) > limit else "")


def split_sentences(text: str) -> List[str]:
    return [s.strip() for s in re.split(r"(?<=[.!?])\s+", re.sub(r"\s+", " ", text).strip()) if s.strip()]


def template_generate(course_slug: str, chapter_slug: str, segment_slug: str, title: str, body: str, tags: List[str], next_title: str) -> ActivationLesson:
    sentences = split_sentences(body)
    lead = sentences[0] if sentences else f"{title} introduces an important civic concept."
    second = " ".join(sentences[1:3]) if len(sentences) > 1 else f"This lesson helps explain how the topic connects to real civic processes."
    summary = summarize_text(body, 220)

    actions = [
        f"Write down one key idea you learned from {title}.",
        f"Identify one local office, meeting, or public process connected to this topic.",
        f"Share or discuss one practical takeaway from this lesson with another person."
    ]

    return ActivationLesson(
        source_path=f"content/courses/{course_slug}/{chapter_slug}/segments/{segment_slug}.md",
        course_slug=course_slug,
        chapter_slug=chapter_slug,
        segment_slug=segment_slug,
        title=title,
        hook=lead,
        reality=second if second else summary,
        actions=actions,
        reflection=f"What part of {title.lower()} feels most relevant to your community or local experience?",
        next_step=next_title or "Continue to the next lesson in this chapter.",
        tags=tags,
        generated_by="template"
    )


def openai_generate(course_slug: str, chapter_slug: str, segment_slug: str, title: str, body: str, tags: List[str], next_title: str, config: Dict) -> ActivationLesson:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY is not set. Use --mode template or set your API key.")

    try:
        from openai import OpenAI
    except Exception as exc:
        raise RuntimeError("openai package is not installed. Install it with: pip install openai") from exc

    client = OpenAI(api_key=api_key)
    prompt_template = PROMPT_PATH.read_text(encoding="utf-8") if PROMPT_PATH.exists() else ""
    prompt = prompt_template.format(
        organization_name=config.get("organization_name", "Stand Up Arkansas"),
        audience=config.get("audience", "Arkansas civic learners"),
        course_slug=course_slug,
        chapter_slug=chapter_slug,
        segment_slug=segment_slug,
        title=title,
        tags=", ".join(tags),
        next_title=next_title or "Continue to the next lesson",
        source_text=body[:12000],
    )

    response = client.responses.create(
        model=os.getenv("OPENAI_MODEL", "gpt-4.1"),
        input=prompt,
        temperature=0.5,
    )

    text = getattr(response, "output_text", "").strip()
    if not text:
        raise RuntimeError("OpenAI returned an empty response.")

    try:
        parsed = json.loads(text)
    except json.JSONDecodeError as exc:
        raise RuntimeError("OpenAI response was not valid JSON. Inspect the raw response and prompt.") from exc

    return ActivationLesson(
        source_path=f"content/courses/{course_slug}/{chapter_slug}/segments/{segment_slug}.md",
        course_slug=course_slug,
        chapter_slug=chapter_slug,
        segment_slug=segment_slug,
        title=parsed.get("title", title),
        hook=parsed.get("hook", ""),
        reality=parsed.get("reality", ""),
        actions=parsed.get("actions", [])[:5],
        reflection=parsed.get("reflection", ""),
        next_step=parsed.get("next_step", next_title or "Continue to the next lesson."),
        tags=parsed.get("tags", tags),
        generated_by="openai"
    )


def render_markdown(lesson: ActivationLesson) -> str:
    action_lines = "\n".join(f"- {item}" for item in lesson.actions)
    tag_line = ", ".join(lesson.tags) if lesson.tags else "none"
    return f"""# {lesson.title}

**Source:** `{lesson.source_path}`  
**Generated by:** `{lesson.generated_by}`  
**Tags:** {tag_line}

## HOOK
{lesson.hook}

## REALITY
{lesson.reality}

## ACTION
{action_lines}

## REFLECTION
{lesson.reflection}

## NEXT
{lesson.next_step}
"""


def gather_segments(course_filter: Optional[str], chapter_filter: Optional[str]) -> List[Dict]:
    rows = []
    if not COURSES_DIR.exists():
        raise SystemExit(f"Courses directory not found: {COURSES_DIR}")

    course_dirs = [p for p in sorted(COURSES_DIR.iterdir()) if p.is_dir() and p.name.startswith("course_")]
    for course_dir in course_dirs:
        if course_filter and course_dir.name != course_filter:
            continue

        chapter_dirs = [p for p in sorted(course_dir.glob("chapter_*")) if p.is_dir() and (p / "segments").exists()]
        for chapter_dir in chapter_dirs:
            if chapter_filter and chapter_dir.name != chapter_filter:
                continue

            segment_paths = sorted((chapter_dir / "segments").glob("*.md"))
            for i, segment_path in enumerate(segment_paths):
                text = segment_path.read_text(encoding="utf-8")
                meta, body = parse_frontmatter(text)
                title = extract_title(meta, body, segment_path.stem)
                tags = meta.get("tags", [])
                if isinstance(tags, str):
                    tags = [tags]
                next_title = ""
                if i + 1 < len(segment_paths):
                    next_text = segment_paths[i + 1].read_text(encoding="utf-8")
                    next_meta, next_body = parse_frontmatter(next_text)
                    next_title = extract_title(next_meta, next_body, segment_paths[i + 1].stem)

                rows.append({
                    "course_slug": course_dir.name,
                    "chapter_slug": chapter_dir.name,
                    "segment_slug": segment_path.stem,
                    "title": title,
                    "body": body,
                    "tags": tags,
                    "next_title": next_title,
                })
    return rows


def write_outputs(lessons: List[ActivationLesson], course_filter: Optional[str], chapter_filter: Optional[str], mode: str) -> None:
    stamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
    suffix = "__".join([x for x in [course_filter, chapter_filter, mode, stamp] if x])
    bundle_dir = OUTPUT_DIR / suffix
    bundle_dir.mkdir(parents=True, exist_ok=True)

    json_payload = {
        "generated_at": datetime.now(UTC).isoformat(),
        "mode": mode,
        "lesson_count": len(lessons),
        "lessons": [asdict(item) for item in lessons],
    }

    (bundle_dir / "activation_lessons.json").write_text(json.dumps(json_payload, indent=2, ensure_ascii=False), encoding="utf-8")

    md_dir = bundle_dir / "markdown"
    md_dir.mkdir(exist_ok=True)
    for idx, lesson in enumerate(lessons, start=1):
        filename = f"{idx:03}_{lesson.segment_slug}.md"
        (md_dir / filename).write_text(render_markdown(lesson), encoding="utf-8")

    manifest = {
        "bundle_dir": str(bundle_dir.relative_to(ROOT)).replace("\\", "/"),
        "json_file": str((bundle_dir / "activation_lessons.json").relative_to(ROOT)).replace("\\", "/"),
        "markdown_dir": str(md_dir.relative_to(ROOT)).replace("\\", "/"),
        "lesson_count": len(lessons),
    }
    (bundle_dir / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")

    print("\n=== PHASE 13 AI GENERATION COMPLETE ===")
    print(f"Mode:        {mode}")
    print(f"Lessons:     {len(lessons)}")
    print(f"Bundle dir:  {bundle_dir}")
    print(f"JSON:        {bundle_dir / 'activation_lessons.json'}")
    print(f"Markdown:    {md_dir}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--course", help="Course slug like course_01_civic_awakening")
    parser.add_argument("--chapter", help="Chapter slug like chapter_01")
    parser.add_argument("--all", action="store_true", help="Generate for all courses and chapters")
    parser.add_argument("--mode", choices=["template", "openai"], default="template")
    args = parser.parse_args()

    if not args.all and not args.course:
        raise SystemExit("Provide --course <slug> or use --all")

    config = load_config()
    rows = gather_segments(None if args.all else args.course, args.chapter)

    if not rows:
        raise SystemExit("No matching segments found.")

    lessons: List[ActivationLesson] = []
    for row in rows:
        if args.mode == "openai":
            lesson = openai_generate(
                row["course_slug"], row["chapter_slug"], row["segment_slug"],
                row["title"], row["body"], row["tags"], row["next_title"], config
            )
        else:
            lesson = template_generate(
                row["course_slug"], row["chapter_slug"], row["segment_slug"],
                row["title"], row["body"], row["tags"], row["next_title"]
            )
        lessons.append(lesson)

    write_outputs(lessons, None if args.all else args.course, args.chapter, args.mode)


if __name__ == "__main__":
    main()
