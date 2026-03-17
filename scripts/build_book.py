from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

CONTENT_DIR = ROOT / "content" / "courses"
EXPORT_DIR = ROOT / "exports" / "book"

EXPORT_DIR.mkdir(parents=True, exist_ok=True)

OUTPUT_FILE = EXPORT_DIR / "compiled_book.md"


def collect_segments():
    segments = []

    for course in sorted(CONTENT_DIR.glob("course_*")):
        for chapter in sorted(course.glob("chapter_*")):
            seg_dir = chapter / "segments"

            if not seg_dir.exists():
                continue

            for seg in sorted(seg_dir.glob("*.md")):
                segments.append(seg)

    return segments


def build_book():
    segments = collect_segments()

    with open(OUTPUT_FILE, "w", encoding="utf-8") as outfile:

        outfile.write("# Arkansas Civics\n\n")

        for seg in segments:

            with open(seg, "r", encoding="utf-8") as infile:
                content = infile.read()

            outfile.write(content)
            outfile.write("\n\n")


def main():

    print("Building compiled book...\n")

    build_book()

    print("Book generated at:")
    print(OUTPUT_FILE)


if __name__ == "__main__":
    main()