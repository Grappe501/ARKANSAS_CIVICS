from __future__ import annotations

from pathlib import Path
from datetime import datetime
import json
import os
import re
import sys
import logging

try:
    import yaml
except ImportError:
    raise SystemExit("PyYAML is required. Install with: pip install pyyaml")

try:
    from openai import OpenAI
except ImportError:
    raise SystemExit("OpenAI Python SDK is required. Install with: pip install openai")


# --------------------------------------------------
# Core Paths
# --------------------------------------------------

ROOT = Path(__file__).resolve().parents[1]

CONFIG_DIR = ROOT / "config" / "course_factory"
CONTENT_DIR = ROOT / "content" / "courses"
EXPORT_DIR = ROOT / "exports" / "ai_course_designer"

EXPORT_DIR.mkdir(parents=True, exist_ok=True)


# --------------------------------------------------
# Logging
# --------------------------------------------------

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)

log = logging.getLogger("ai_course_designer")


# --------------------------------------------------
# OpenAI
# --------------------------------------------------

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "").strip()
OPENAI_MODEL = os.getenv("OPENAI_COURSE_MODEL", "gpt-5")

client = OpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None


# --------------------------------------------------
# Utility
# --------------------------------------------------

def clean_title(text: str) -> str:
    return text.replace("_", " ").title()


def slug(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", text.lower()).strip("_")


def load_yaml(path: Path) -> dict:
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def word_count(text: str) -> int:
    return len(text.split())


def now_iso() -> str:
    return datetime.utcnow().isoformat() + "Z"


# --------------------------------------------------
# Course Reading
# --------------------------------------------------

def validate_course_config(cfg: dict) -> None:
    required = ["course_id", "chapters"]
    for key in required:
        if key not in cfg:
            raise ValueError(f"Missing required field: {key}")

    if not isinstance(cfg["chapters"], list):
        raise ValueError("chapters must be a list")

    for chapter in cfg["chapters"]:
        if "chapter_id" not in chapter:
            raise ValueError("chapter missing chapter_id")
        if "segments" not in chapter:
            raise ValueError(f"{chapter['chapter_id']} missing segments")


def read_segment(course_id: str, chapter_id: str, segment_name: str) -> str:
    path = CONTENT_DIR / course_id / chapter_id / "segments" / segment_name
    if not path.exists():
        log.warning("Missing segment: %s", path)
        return f"[Missing segment: {segment_name}]"
    return read_text(path)


def collect_lessons(course_cfg: dict) -> list[dict]:
    course_id = course_cfg["course_id"]
    lessons: list[dict] = []

    for lesson_number, chapter in enumerate(course_cfg["chapters"], start=1):
        chapter_id = chapter["chapter_id"]
        title = chapter.get("title", clean_title(chapter_id))
        segment_names = chapter.get("segments", [])

        parts = [read_segment(course_id, chapter_id, seg) for seg in segment_names]
        body = "\n\n".join(parts).strip()

        lessons.append(
            {
                "lesson_number": lesson_number,
                "chapter_id": chapter_id,
                "title": title,
                "segments": segment_names,
                "body": body,
                "word_count": word_count(body),
            }
        )

    return lessons


# --------------------------------------------------
# Diagnostics
# --------------------------------------------------

def diagnose_lesson(lesson: dict) -> dict:
    issues = []
    strengths = []

    wc = lesson["word_count"]
    body = lesson["body"].lower()

    if wc < 350:
        issues.append("Lesson is too short for a strong self-guided learning experience.")
    elif wc < 700:
        issues.append("Lesson may need deeper examples, interactions, or explanation.")
    else:
        strengths.append("Lesson has a reasonable content base.")

    if "arkansas" not in body:
        issues.append("Lesson may need stronger Arkansas-specific framing.")
    else:
        strengths.append("Lesson includes Arkansas framing.")

    if "question" not in body and "reflection" not in body:
        issues.append("Lesson may need learner reflection prompts.")
    else:
        strengths.append("Lesson appears to include reflective elements.")

    if "scenario" not in body and "example" not in body:
        issues.append("Lesson may need applied examples or scenarios.")
    else:
        strengths.append("Lesson appears to include examples or application.")

    return {
        "lesson_number": lesson["lesson_number"],
        "title": lesson["title"],
        "word_count": wc,
        "issues": issues,
        "strengths": strengths,
    }


# --------------------------------------------------
# Prompt Builders
# --------------------------------------------------

def build_system_prompt() -> str:
    return (
        "You are a senior instructional designer, civic educator, political organizer, "
        "and Arkansas-focused curriculum architect. "
        "Your job is to transform course materials into rich, practical, interactive, "
        "Articulate-ready learning assets. "
        "Always make lessons concrete, scenario-based, Arkansas-specific where possible, "
        "and built for adult/youth civic engagement. "
        "Write with clarity, warmth, authority, and practical usefulness."
    )


def build_lesson_prompt(course_cfg: dict, lesson: dict, diagnosis: dict) -> str:
    return f"""
Design a complete lesson package for a civic engagement course.

COURSE
Title: {course_cfg.get("title", clean_title(course_cfg["course_id"]))}
Subtitle: {course_cfg.get("subtitle", "")}
Description: {course_cfg.get("description", "")}
Duration target: {course_cfg.get("duration_minutes", 90)} minutes

LESSON
Lesson number: {lesson["lesson_number"]}
Chapter ID: {lesson["chapter_id"]}
Lesson title: {lesson["title"]}
Current word count: {lesson["word_count"]}

CURRENT LESSON CONTENT
{lesson["body"]}

DIAGNOSTIC ISSUES
{json.dumps(diagnosis["issues"], indent=2)}

TASK
Generate a state-of-the-art instructional design package for this lesson.

Return these sections in this exact order:

## LESSON_OVERVIEW
A short overview of the lesson’s purpose and learner transformation.

## LEARNING_OBJECTIVES
5 strong measurable learning objectives.

## EXPANDED_LESSON_DRAFT
A richly expanded lesson draft suitable for Articulate AI import.
Include:
- strong intro
- Arkansas-specific framing
- 3-5 subsections
- real examples
- practical transitions
- engaging summary

## RISE_BUILD_PLAN
A detailed Articulate Rise build plan.
Specify suggested blocks in sequence.

## SCENARIO_ACTIVITY
A branching or decision-based activity.

## KNOWLEDGE_CHECKS
At least 8 questions with answer keys.

## WORKBOOK_EXERCISES
At least 5 workbook prompts or exercises.

## FACILITATOR_NOTES
Facilitator guidance for live delivery.

## MEDIA_PROMPTS
Specific image / diagram / map prompt ideas.

## ARKANSAS_CONTEXT_INSERTS
Specific Arkansas stories, institutions, or examples that could deepen the lesson.

## IMPROVEMENT_NOTES
What was weak in the original lesson and how this package fixes it.
"""


# --------------------------------------------------
# OpenAI Call
# --------------------------------------------------

def call_openai(prompt: str) -> str:
    if not client:
        raise RuntimeError("OPENAI_API_KEY is not set.")

    response = client.responses.create(
        model=OPENAI_MODEL,
        input=[
            {"role": "system", "content": build_system_prompt()},
            {"role": "user", "content": prompt},
        ],
    )

    output_text = getattr(response, "output_text", None)
    if output_text:
        return output_text

    # fallback for SDK / API shape changes
    try:
        pieces = []
        for item in response.output:
            content = getattr(item, "content", None)
            if not content:
                continue
            for part in content:
                text_value = getattr(part, "text", None)
                if text_value:
                    pieces.append(text_value)
        return "\n".join(pieces).strip()
    except Exception:
        return str(response)


# --------------------------------------------------
# File Writers
# --------------------------------------------------

def write_lesson_bundle(
    course_cfg: dict,
    lesson: dict,
    diagnosis: dict,
    ai_output: str,
    course_out_dir: Path,
) -> None:
    lesson_slug = f"lesson_{lesson['lesson_number']:02d}_{slug(lesson['title'])}"
    lesson_dir = course_out_dir / lesson_slug
    lesson_dir.mkdir(parents=True, exist_ok=True)

    write_text(lesson_dir / "source_lesson.md", lesson["body"])
    write_text(lesson_dir / "ai_designed_lesson.md", ai_output)
    write_text(
        lesson_dir / "diagnostics.json",
        json.dumps(diagnosis, indent=2),
    )

    articulate_ai_import = (
        f"COURSE TITLE: {course_cfg.get('title', clean_title(course_cfg['course_id']))}\n"
        f"LESSON TITLE: {lesson['title']}\n\n"
        f"{ai_output}"
    )
    write_text(lesson_dir / "articulate_ai_import.txt", articulate_ai_import)

    request_payload = {
        "course": course_cfg["course_id"],
        "chapter": lesson["chapter_id"],
        "segment": f"lesson_{lesson['lesson_number']:02d}",
        "content": lesson["body"],
        "instruction": "Use the AI-designed lesson package as the basis for a Rise-ready build.",
        "generated_at": now_iso(),
    }
    write_text(
        lesson_dir / "rise_request.json",
        json.dumps(request_payload, indent=2),
    )


def write_course_summary(course_cfg: dict, diagnoses: list[dict], out_dir: Path) -> None:
    summary = {
        "course_id": course_cfg["course_id"],
        "title": course_cfg.get("title", clean_title(course_cfg["course_id"])),
        "subtitle": course_cfg.get("subtitle", ""),
        "description": course_cfg.get("description", ""),
        "generated_at": now_iso(),
        "lesson_diagnostics": diagnoses,
    }
    write_text(out_dir / "course_diagnostics.json", json.dumps(summary, indent=2))

    md_lines = [
        f"# AI Course Designer Summary — {summary['title']}",
        "",
        summary["description"],
        "",
        "## Lesson Diagnostics",
        "",
    ]

    for diag in diagnoses:
        md_lines.append(f"## Lesson {diag['lesson_number']}: {diag['title']}")
        md_lines.append("")
        md_lines.append(f"- Word Count: {diag['word_count']}")
        if diag["issues"]:
            md_lines.append("- Issues:")
            for issue in diag["issues"]:
                md_lines.append(f"  - {issue}")
        if diag["strengths"]:
            md_lines.append("- Strengths:")
            for strength in diag["strengths"]:
                md_lines.append(f"  - {strength}")
        md_lines.append("")

    write_text(out_dir / "course_diagnostics.md", "\n".join(md_lines))


# --------------------------------------------------
# Main Course Designer
# --------------------------------------------------

def design_course(config_path: Path) -> None:
    course_cfg = load_yaml(config_path)
    validate_course_config(course_cfg)

    course_id = course_cfg["course_id"]
    lessons = collect_lessons(course_cfg)

    out_dir = EXPORT_DIR / course_id
    out_dir.mkdir(parents=True, exist_ok=True)

    diagnoses = []

    for lesson in lessons:
        diagnosis = diagnose_lesson(lesson)
        diagnoses.append(diagnosis)

        prompt = build_lesson_prompt(course_cfg, lesson, diagnosis)

        if client:
            log.info("Designing lesson %s for %s with OpenAI", lesson["lesson_number"], course_id)
            ai_output = call_openai(prompt)
        else:
            log.warning("OPENAI_API_KEY not set; writing prompt-only package for %s lesson %s", course_id, lesson["lesson_number"])
            ai_output = (
                "# AI output unavailable\n\n"
                "OPENAI_API_KEY is not set. Use the prompt below manually or set the key.\n\n"
                "## PROMPT\n\n"
                f"{prompt}"
            )

        write_lesson_bundle(course_cfg, lesson, diagnosis, ai_output, out_dir)

    write_course_summary(course_cfg, diagnoses, out_dir)

    log.info("Completed AI course design for %s", course_id)


# --------------------------------------------------
# Entry
# --------------------------------------------------

def main() -> None:
    config_files = sorted(CONFIG_DIR.glob("course_*.yaml"))

    if not config_files:
        log.warning("No course configs found in %s", CONFIG_DIR)
        return

    for config_path in config_files:
        design_course(config_path)

    print("")
    print("AI Course Designer complete.")
    print(f"Output root: {EXPORT_DIR}")
    print("")


if __name__ == "__main__":
    main()