from pathlib import Path
import json
import subprocess
import sys
import logging
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

SCRIPT_DIR = ROOT / "scripts"

EXPORT_RISE_SCRIPT = SCRIPT_DIR / "export_rise_course.py"
EXPORT_SCORM_SCRIPT = SCRIPT_DIR / "generate_scorm_course.py"
COPY_DASHBOARD_SCRIPT = SCRIPT_DIR / "copy_dashboard_content.py"
BUILD_ALL_SCRIPT = SCRIPT_DIR / "build_all.py"

EXPORT_ROOT.mkdir(parents=True, exist_ok=True)
SUITE_DIR.mkdir(parents=True, exist_ok=True)


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

def validate_course_config(cfg: dict):

    required = ["course_id", "chapters"]

    for r in required:
        if r not in cfg:
            raise ValueError(f"Missing required field: {r}")

    if not isinstance(cfg["chapters"], list):
        raise ValueError("chapters must be a list")

    for c in cfg["chapters"]:
        if "chapter_id" not in c:
            raise ValueError("chapter missing chapter_id")

        if "segments" not in c:
            raise ValueError(f"{c['chapter_id']} missing segments")


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

        lessons.append(
            {
                "lesson_number": idx,
                "chapter_id": chapter_id,
                "title": chapter_title,
                "segment_count": len(segments),
                "body": body,
                "word_count": len(body.split())
            }
        )

    return lessons


# --------------------------------------------------
# Course Payload
# --------------------------------------------------

def build_course_payload(cfg, lessons):

    return {
        "course": cfg["course_id"],
        "title": cfg.get("title", clean_title(cfg["course_id"])),
        "subtitle": cfg.get("subtitle", ""),
        "description": cfg.get("description", ""),
        "duration_minutes": cfg.get("duration_minutes", 90),
        "lesson_count": len(lessons),
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "lessons": lessons
    }


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
        lines.append(f"Segments: {lesson['segment_count']}")
        lines.append("")
        lines.append("Suggested Rise Flow")
        lines.append("1. Intro")
        lines.append("2. Concept")
        lines.append("3. Arkansas Example")
        lines.append("4. Reflection")
        lines.append("5. Knowledge Check")
        lines.append("6. Scenario")
        lines.append("7. Summary")
        lines.append("")

    return "\n".join(lines)


def build_facilitator(payload):

    lines = []

    lines.append(f"# Facilitator Guide — {payload['title']}")
    lines.append("")

    for lesson in payload["lessons"]:

        lines.append(f"## Lesson {lesson['lesson_number']}: {lesson['title']}")
        lines.append("")
        lines.append("Facilitator Goals")
        lines.append("- connect lesson to Arkansas civic life")
        lines.append("- prompt discussion")
        lines.append("- drive practical civic action")
        lines.append("")
        lines.append("Discussion Questions")
        lines.append("- what stood out?")
        lines.append("- how does this show up locally?")
        lines.append("- what should citizens do?")
        lines.append("")

    return "\n".join(lines)


def build_workbook(payload):

    lines = []

    lines.append(f"# Workbook — {payload['title']}")
    lines.append("")

    for lesson in payload["lessons"]:

        lines.append(f"## Lesson {lesson['lesson_number']}: {lesson['title']}")
        lines.append("")
        lines.append("Reflection")
        lines.append("1. What concept surprised you?")
        lines.append("2. Where does this appear locally?")
        lines.append("3. What action would you take?")
        lines.append("")
        lines.append("Application")
        lines.append("Write one civic action step.")
        lines.append("")

    return "\n".join(lines)


def build_quiz(payload):

    lines = []

    lines.append(f"# Quiz Bank — {payload['title']}")
    lines.append("")

    for lesson in payload["lessons"]:

        lines.append(f"## Lesson {lesson['lesson_number']}")
        lines.append("")

        for q in range(1, 6):

            lines.append(f"Question {q}")
            lines.append("What is the most important concept from this lesson?")
            lines.append("")
            lines.append("A. Distractor")
            lines.append("B. Distractor")
            lines.append("C. Correct")
            lines.append("D. Distractor")
            lines.append("")

    return "\n".join(lines)


# --------------------------------------------------
# Rise Request Builder
# --------------------------------------------------

def write_rise_requests(payload, out_dir):

    req_dir = out_dir / "rise_requests"
    req_dir.mkdir(parents=True, exist_ok=True)

    for lesson in payload["lessons"]:

        request = {
            "course": payload["course"],
            "chapter": lesson["chapter_id"],
            "segment": f"lesson_{lesson['lesson_number']}",
            "content": lesson["body"],
            "instruction": (
                "Generate a Rise-ready civic education lesson with headings, "
                "Arkansas examples, a scenario interaction, knowledge check, "
                "reflection prompt, and summary."
            )
        }

        path = req_dir / f"lesson_{lesson['lesson_number']:02d}.json"

        path.write_text(json.dumps(request, indent=2))

        run_python(EXPORT_RISE_SCRIPT, str(path))


# --------------------------------------------------
# Course Export
# --------------------------------------------------

def export_course(config_path):

    cfg = load_yaml(config_path)

    validate_course_config(cfg)

    lessons = collect_lessons(cfg)

    payload = build_course_payload(cfg, lessons)

    course_dir = SUITE_DIR / cfg["course_id"]
    course_dir.mkdir(parents=True, exist_ok=True)

    log.info(f"Generating suite for {cfg['course_id']}")

    (course_dir / "course_manifest.json").write_text(json.dumps(payload, indent=2))
    (course_dir / "outline.md").write_text(build_outline(payload))
    (course_dir / "facilitator_guide.md").write_text(build_facilitator(payload))
    (course_dir / "workbook.md").write_text(build_workbook(payload))
    (course_dir / "quiz_bank.md").write_text(build_quiz(payload))

    write_rise_requests(payload, course_dir)

    if EXPORT_SCORM_SCRIPT.exists():
        run_python(EXPORT_SCORM_SCRIPT)

    summary = {
        "course": payload["course"],
        "title": payload["title"],
        "lessons": payload["lesson_count"],
        "generated": payload["generated_at"]
    }

    (course_dir / "factory_summary.json").write_text(json.dumps(summary, indent=2))

    log.info(f"Completed {cfg['course_id']}")


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
# Main
# --------------------------------------------------

def main():

    configs = sorted(CONFIG_DIR.glob("course_*.yaml"))

    if not configs:
        log.warning("No course configs found")
        return

    for cfg in configs:
        export_course(cfg)

    refresh_platform()

    log.info("Course factory pipeline complete")


if __name__ == "__main__":
    main()