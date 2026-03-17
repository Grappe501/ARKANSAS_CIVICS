from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[1]

CONTENT_DIR = ROOT / "content" / "courses"
EXPORT_DIR = ROOT / "exports" / "course"

EXPORT_DIR.mkdir(parents=True, exist_ok=True)

OUTPUT_FILE = EXPORT_DIR / "course_manifest.json"


def collect_courses():

    courses = []

    for course in sorted(CONTENT_DIR.glob("course_*")):

        course_data = {
            "course": course.name,
            "chapters": []
        }

        for chapter in sorted(course.glob("chapter_*")):

            chapter_data = {
                "chapter": chapter.name,
                "segments": []
            }

            seg_dir = chapter / "segments"

            if seg_dir.exists():

                for seg in sorted(seg_dir.glob("*.md")):
                    chapter_data["segments"].append(seg.name)

            course_data["chapters"].append(chapter_data)

        courses.append(course_data)

    return courses


def build_course_manifest():

    courses = collect_courses()

    with open(OUTPUT_FILE, "w", encoding="utf-8") as outfile:
        json.dump(courses, outfile, indent=2)


def main():

    print("Building course manifest...\n")

    build_course_manifest()

    print("Course manifest generated at:")
    print(OUTPUT_FILE)


if __name__ == "__main__":
    main()