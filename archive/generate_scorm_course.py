from pathlib import Path
import json
import zipfile
import re

ROOT = Path(__file__).resolve().parents[1]

CONTENT_DIR = ROOT / "content" / "courses"
EXPORT_DIR = ROOT / "exports" / "articulate" / "scorm"


def slug(text):
    text = text.lower()
    text = re.sub(r"[^a-z0-9]+", "_", text)
    return text.strip("_")


def read_segments(course_path):

    lessons = []

    chapters = sorted(course_path.glob("chapter_*"))

    for chapter in chapters:

        seg_dir = chapter / "segments"

        if not seg_dir.exists():
            continue

        segments = sorted(seg_dir.glob("*.md"))

        text = ""

        for seg in segments:
            text += seg.read_text(encoding="utf-8") + "\n\n"

        lessons.append(text)

    return lessons


def build_lesson_html(title, body):

    return f"""
<html>
<head>
<meta charset="utf-8">
<title>{title}</title>
</head>

<body>

<h1>{title}</h1>

<div>

{body.replace("\n","<br>")}

</div>

</body>
</html>
"""


def build_manifest(course_name, lesson_count):

    items = ""

    for i in range(lesson_count):
        items += f"""
        <item identifier="lesson{i+1}" identifierref="res{i+1}">
            <title>Lesson {i+1}</title>
        </item>
        """

    resources = ""

    for i in range(lesson_count):
        resources += f"""
        <resource identifier="res{i+1}" type="webcontent" href="lessons/lesson_{i+1}.html">
            <file href="lessons/lesson_{i+1}.html"/>
        </resource>
        """

    return f"""
<manifest identifier="{course_name}">

<organizations default="org1">
<organization identifier="org1">

{items}

</organization>
</organizations>

<resources>

{resources}

</resources>

</manifest>
"""


def build_quiz_bank(lesson_count):

    questions = []

    for i in range(lesson_count):

        questions.append(f"""
Lesson {i+1}

1. What is the key concept of this lesson?

A. Option A
B. Option B
C. Option C
D. Option D

2. Which civic action best reflects the lesson principle?

A. Option A
B. Option B
C. Option C
D. Option D
""")

    return "\n".join(questions)


def build_facilitator_guide(course):

    return f"""
FACILITATOR GUIDE

Course:
{course}

Use discussion questions after each lesson.

Encourage learners to connect lesson topics to
real civic participation in their communities.

Each lesson should include:

• discussion
• scenario exercise
• reflection writing
"""


def build_workbook(course):

    return f"""
WORKBOOK

Course:
{course}

Reflection Questions

1. What concept from this lesson surprised you?
2. How does this issue affect your community?
3. What civic action could address this problem?
"""


def build_build_plan(course):

    return f"""
COURSE BUILD PLAN

Course:
{course}

Recommended Rise Structure

Lesson Page
Text Block
Scenario Interaction
Knowledge Check
Reflection Exercise
Summary
"""


def export_course(course_dir):

    course_name = course_dir.name

    lessons = read_segments(course_dir)

    if not lessons:
        print("No lessons found")
        return

    course_export = EXPORT_DIR / course_name
    lessons_dir = course_export / "lessons"

    lessons_dir.mkdir(parents=True, exist_ok=True)

    lesson_html_files = []

    for i, lesson_text in enumerate(lessons):

        lesson_title = f"{course_name} Lesson {i+1}"

        html = build_lesson_html(lesson_title, lesson_text)

        file_path = lessons_dir / f"lesson_{i+1}.html"

        file_path.write_text(html, encoding="utf-8")

        lesson_html_files.append(file_path)

    manifest = build_manifest(course_name, len(lessons))

    (course_export / "imsmanifest.xml").write_text(manifest)

    (course_export / "quiz_bank.md").write_text(
        build_quiz_bank(len(lessons))
    )

    (course_export / "facilitator_guide.md").write_text(
        build_facilitator_guide(course_name)
    )

    (course_export / "workbook.md").write_text(
        build_workbook(course_name)
    )

    (course_export / "build_plan.md").write_text(
        build_build_plan(course_name)
    )

    zip_path = EXPORT_DIR / f"{course_name}_SCORM.zip"

    with zipfile.ZipFile(zip_path, "w") as z:

        for file in course_export.rglob("*"):
            z.write(file, file.relative_to(course_export))

    print(f"SCORM package created: {zip_path}")


def main():

    EXPORT_DIR.mkdir(parents=True, exist_ok=True)

    courses = CONTENT_DIR.glob("course_*")

    for course in courses:
        export_course(course)


if __name__ == "__main__":
    main()