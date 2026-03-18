from pathlib import Path
import json
import subprocess
import sys
import logging
import hashlib
import concurrent.futures
import time
from datetime import datetime

try:
    import yaml
except ImportError:
    raise SystemExit("PyYAML required. Install with: pip install pyyaml")


# --------------------------------------------------
# Core Paths
# --------------------------------------------------

ROOT = Path(__file__).resolve().parents[1]

CONFIG_DIR = ROOT / "config" / "course_factory"
CONTENT_DIR = ROOT / "content" / "courses"

EXPORT_ROOT = ROOT / "exports" / "course_factory"
SUITE_DIR = EXPORT_ROOT / "suite"

CACHE_DIR = EXPORT_ROOT / "_cache"

SCRIPT_DIR = ROOT / "scripts"

EXPORT_RISE_SCRIPT = SCRIPT_DIR / "export_rise_course.py"
EXPORT_SCORM_SCRIPT = SCRIPT_DIR / "generate_scorm_course.py"
COPY_DASHBOARD_SCRIPT = SCRIPT_DIR / "copy_dashboard_content.py"
BUILD_ALL_SCRIPT = SCRIPT_DIR / "build_all.py"
CURRICULUM_INTEL_SCRIPT = SCRIPT_DIR / "generate_curriculum_intelligence_layer.py"
AI_DESIGNER_SCRIPT = SCRIPT_DIR / "ai_course_designer.py"

EXPORT_ROOT.mkdir(parents=True, exist_ok=True)
SUITE_DIR.mkdir(parents=True, exist_ok=True)
CACHE_DIR.mkdir(parents=True, exist_ok=True)


# --------------------------------------------------
# Logging
# --------------------------------------------------

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)

log = logging.getLogger("course_factory")


# --------------------------------------------------
# Utilities
# --------------------------------------------------

def slug(text: str) -> str:
    return "".join(c if c.isalnum() else "_" for c in text.lower()).strip("_")


def clean_title(text: str) -> str:
    return text.replace("_", " ").title()


def load_yaml(path: Path) -> dict:
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def hash_content(text: str):
    return hashlib.sha256(text.encode()).hexdigest()


def now_iso():
    return datetime.utcnow().isoformat() + "Z"


def run_python(script: Path, *args):

    if not script.exists():
        log.warning(f"Script missing: {script}")
        return

    cmd = [sys.executable, str(script), *args]

    try:
        subprocess.run(cmd, cwd=ROOT, check=True)
    except subprocess.CalledProcessError as e:
        log.error(f"Script failed: {script}")
        raise e


# --------------------------------------------------
# Validation
# --------------------------------------------------

def validate_course_config(cfg):

    required = ["course_id", "chapters"]

    for r in required:
        if r not in cfg:
            raise ValueError(f"Missing required field: {r}")

    if not isinstance(cfg["chapters"], list):
        raise ValueError("chapters must be a list")

    for chapter in cfg["chapters"]:

        if "chapter_id" not in chapter:
            raise ValueError("chapter missing chapter_id")

        if "segments" not in chapter:
            raise ValueError(f"{chapter['chapter_id']} missing segments")


# --------------------------------------------------
# Segment Reading
# --------------------------------------------------

def read_segment(course, chapter, segment):

    seg = CONTENT_DIR / course / chapter / "segments" / segment

    if not seg.exists():
        log.warning(f"Missing segment: {seg}")
        return f"[Missing segment: {segment}]"

    return seg.read_text(encoding="utf-8")


# --------------------------------------------------
# Lesson Builder
# --------------------------------------------------

def collect_lessons(course_cfg):

    course_id = course_cfg["course_id"]

    lessons = []

    for idx, chapter in enumerate(course_cfg["chapters"], start=1):

        chapter_id = chapter["chapter_id"]
        chapter_title = chapter.get("title", clean_title(chapter_id))
        segments = chapter["segments"]

        bodies = []

        for seg in segments:
            bodies.append(read_segment(course_id, chapter_id, seg))

        body = "\n\n".join(bodies)

        word_count = len(body.split())

        complexity_score = min(10, int(word_count / 300))

        lessons.append(
            {
                "lesson_number": idx,
                "chapter_id": chapter_id,
                "title": chapter_title,
                "segment_count": len(segments),
                "body": body,
                "word_count": word_count,
                "complexity_score": complexity_score,
                "content_hash": hash_content(body),
            }
        )

    return lessons


# --------------------------------------------------
# Course Payload
# --------------------------------------------------

def build_course_payload(cfg, lessons):

    total_words = sum(l["word_count"] for l in lessons)

    return {
        "course": cfg["course_id"],
        "title": cfg.get("title", clean_title(cfg["course_id"])),
        "subtitle": cfg.get("subtitle", ""),
        "description": cfg.get("description", ""),
        "duration_minutes": cfg.get("duration_minutes", 90),
        "lesson_count": len(lessons),
        "total_word_count": total_words,
        "average_lesson_words": int(total_words / max(1, len(lessons))),
        "generated_at": now_iso(),
        "lessons": lessons
    }


# --------------------------------------------------
# Diagnostics
# --------------------------------------------------

def run_course_diagnostics(payload):

    issues = []

    for lesson in payload["lessons"]:

        if lesson["word_count"] < 300:
            issues.append(
                f"Lesson {lesson['lesson_number']} appears short ({lesson['word_count']} words)"
            )

        if lesson["segment_count"] == 0:
            issues.append(
                f"Lesson {lesson['lesson_number']} has no segments"
            )

        if lesson["complexity_score"] <= 1:
            issues.append(
                f"Lesson {lesson['lesson_number']} complexity score extremely low"
            )

    return issues


# --------------------------------------------------
# Asset Builders
# --------------------------------------------------

def build_outline(payload):

    lines = []

    lines.append(f"# {payload['title']}")
    lines.append("")
    lines.append(payload["description"])
    lines.append("")

    for lesson in payload["lessons"]:

        lines.append(f"## Lesson {lesson['lesson_number']}: {lesson['title']}")
        lines.append("")

        lines.append(f"Word Count: {lesson['word_count']}")
        lines.append(f"Complexity Score: {lesson['complexity_score']}/10")

        lines.append("")
        lines.append("Suggested Rise Flow")

        lines.append("1. Cover")
        lines.append("2. Civic framing")
        lines.append("3. Core concept")
        lines.append("4. Arkansas example")
        lines.append("5. Scenario")
        lines.append("6. Reflection")
        lines.append("7. Knowledge check")
        lines.append("8. Summary")

        lines.append("")

    return "\n".join(lines)


def build_quiz(payload):

    lines = []

    lines.append(f"# Quiz Bank — {payload['title']}")
    lines.append("")

    for lesson in payload["lessons"]:

        lines.append(f"## Lesson {lesson['lesson_number']}")

        for q in range(1, 6):

            lines.append("")
            lines.append(f"Question {q}")
            lines.append("What is the most important concept from this lesson?")
            lines.append("")
            lines.append("A. Distractor")
            lines.append("B. Distractor")
            lines.append("C. Correct")
            lines.append("D. Distractor")

    return "\n".join(lines)


# --------------------------------------------------
# Rise Request Builder
# --------------------------------------------------

def build_rise_request(payload, lesson):

    return {
        "course": payload["course"],
        "chapter": lesson["chapter_id"],
        "segment": f"lesson_{lesson['lesson_number']}",
        "word_count": lesson["word_count"],
        "complexity_score": lesson["complexity_score"],
        "content": lesson["body"],
        "instruction": (
            "Generate a complete Articulate Rise lesson including:\n"
            "- engaging introduction\n"
            "- Arkansas context\n"
            "- scenario block\n"
            "- interaction\n"
            "- reflection prompt\n"
            "- knowledge check\n"
            "- summary\n"
        )
    }


def write_rise_requests(payload, out_dir):

    req_dir = out_dir / "rise_requests"
    req_dir.mkdir(parents=True, exist_ok=True)

    def process_lesson(lesson):

        request = build_rise_request(payload, lesson)

        path = req_dir / f"lesson_{lesson['lesson_number']:02d}.json"

        path.write_text(json.dumps(request, indent=2))

        run_python(EXPORT_RISE_SCRIPT, str(path))

    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
        executor.map(process_lesson, payload["lessons"])


# --------------------------------------------------
# Course Export
# --------------------------------------------------

def export_course(config_path):

    cfg = load_yaml(config_path)

    validate_course_config(cfg)

    lessons = collect_lessons(cfg)

    payload = build_course_payload(cfg, lessons)

    diagnostics = run_course_diagnostics(payload)

    course_dir = SUITE_DIR / cfg["course_id"]
    course_dir.mkdir(parents=True, exist_ok=True)

    log.info(f"Generating suite for {cfg['course_id']}")

    (course_dir / "course_manifest.json").write_text(json.dumps(payload, indent=2))

    (course_dir / "outline.md").write_text(build_outline(payload))

    (course_dir / "quiz_bank.md").write_text(build_quiz(payload))

    if diagnostics:
        (course_dir / "diagnostics.json").write_text(json.dumps(diagnostics, indent=2))

    write_rise_requests(payload, course_dir)

    if EXPORT_SCORM_SCRIPT.exists():
        run_python(EXPORT_SCORM_SCRIPT)

    summary = {
        "course": payload["course"],
        "title": payload["title"],
        "lessons": payload["lesson_count"],
        "total_words": payload["total_word_count"],
        "generated": payload["generated_at"]
    }

    (course_dir / "factory_summary.json").write_text(json.dumps(summary, indent=2))

    log.info(f"Completed {cfg['course_id']}")


# --------------------------------------------------
# Intelligence Layers
# --------------------------------------------------

def run_curriculum_intelligence():

    if CURRICULUM_INTEL_SCRIPT.exists():

        log.info("Running curriculum intelligence layer")

        run_python(CURRICULUM_INTEL_SCRIPT)


def run_ai_course_designer():

    if AI_DESIGNER_SCRIPT.exists():

        log.info("Running AI course designer")

        run_python(AI_DESIGNER_SCRIPT)


# --------------------------------------------------
# Dashboard Sync
# --------------------------------------------------

def refresh_platform():

    log.info("Refreshing dashboard content")

    if COPY_DASHBOARD_SCRIPT.exists():
        run_python(COPY_DASHBOARD_SCRIPT)

    if BUILD_ALL_SCRIPT.exists():
        run_python(BUILD_ALL_SCRIPT)


# --------------------------------------------------
# Pipeline Metrics
# --------------------------------------------------

def print_pipeline_summary(start_time):

    elapsed = round(time.time() - start_time, 2)

    log.info("Pipeline finished")

    log.info(f"Total runtime: {elapsed} seconds")

    log.info(f"Exports directory: {EXPORT_ROOT}")


# --------------------------------------------------
# Main
# --------------------------------------------------

def main():

    start_time = time.time()

    configs = sorted(CONFIG_DIR.glob("course_*.yaml"))

    if not configs:
        log.warning("No course configs found")
        return

    log.info(f"Processing {len(configs)} course configs")

    for cfg in configs:
        export_course(cfg)

    run_ai_course_designer()

    run_curriculum_intelligence()

    refresh_platform()

    print_pipeline_summary(start_time)


if __name__ == "__main__":
    main()