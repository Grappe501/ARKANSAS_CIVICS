from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONTENT_DIR = ROOT / "content" / "courses"

COURSES = [
    "civic_awakening",
    "arkansas_civic_history",
    "direct_democracy",
    "voting_systems",
    "labor_and_collective_power",
    "shared_pain",
    "shared_purpose",
    "coalition_building",
    "messaging_and_media",
    "strategy_and_campaigns",
    "opposition_and_pushback",
    "sustaining_movements"
]

CHAPTERS_PER_COURSE = 4
SEGMENTS_PER_CHAPTER = 12


SEGMENT_TEMPLATE = """---
title: {title}
course: {course}
chapter: {chapter}
segment: {segment}

tags:
  - civic_engagement
  - arkansas
---

# {title}

## Book Narrative

Write the narrative section of the book here.

## Course Activity

Describe the interactive scenario or exercise.

## Workbook Exercise

Prompt readers to reflect or apply what they learned.

## Workshop Activity

Describe a group activity for live sessions.

## Facilitator Notes

Guidance for workshop facilitators.
"""


def create_segment(path, course, chapter, segment):

    title = f"Segment {segment}"

    content = SEGMENT_TEMPLATE.format(
        title=title,
        course=course,
        chapter=chapter,
        segment=segment
    )

    if not path.exists():
        path.write_text(content, encoding="utf-8")


def scaffold():

    CONTENT_DIR.mkdir(parents=True, exist_ok=True)

    for c_index, course in enumerate(COURSES, start=1):

        course_name = f"course_{c_index:02d}_{course}"
        course_path = CONTENT_DIR / course_name
        course_path.mkdir(exist_ok=True)

        for chapter_num in range(1, CHAPTERS_PER_COURSE + 1):

            chapter_name = f"chapter_{chapter_num:02d}"
            chapter_path = course_path / chapter_name

            segments_path = chapter_path / "segments"

            segments_path.mkdir(parents=True, exist_ok=True)

            for segment_num in range(1, SEGMENTS_PER_CHAPTER + 1):

                segment_file = segments_path / f"{segment_num:02d}_segment.md"

                create_segment(
                    segment_file,
                    course_name,
                    chapter_name,
                    segment_num
                )

    print("\nArkansas Civics Master Scaffold Generated\n")
    print(f"Courses: {len(COURSES)}")
    print(f"Chapters per course: {CHAPTERS_PER_COURSE}")
    print(f"Segments per chapter: {SEGMENTS_PER_CHAPTER}")
    print(f"Total segments: {len(COURSES)*CHAPTERS_PER_COURSE*SEGMENTS_PER_CHAPTER}\n")


if __name__ == "__main__":
    scaffold()