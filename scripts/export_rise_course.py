from pathlib import Path
import json
import sys
import re
from datetime import datetime

ROOT = Path(__file__).resolve().parents[1]

EXPORT_DIR = ROOT / "exports" / "articulate" / "rise"
EXPORT_DIR.mkdir(parents=True, exist_ok=True)


# --------------------------------------------------
# Utility
# --------------------------------------------------

def slug(text):
    text = text.lower()
    text = re.sub(r"[^a-z0-9]+", "_", text)
    return text.strip("_")


def clean_title(text):
    return text.replace("_", " ").title()


def word_count(text):
    return len(text.split())


# --------------------------------------------------
# AI Import File
# --------------------------------------------------

def build_ai_import(title, body, instruction):

    return f"""
COURSE LESSON

Title:
{title}

Lesson Objective:
Students will understand and apply the concepts discussed in this lesson.

Lesson Content:

{body}

Additional Author Notes:

{instruction}

Structure this lesson using:

• Headings
• Key concept callouts
• Knowledge checks
• Scenario examples
• Reflection prompts
"""


# --------------------------------------------------
# Rise Build Plan
# --------------------------------------------------

def build_rise_plan(title, body):

    wc = word_count(body)

    return f"""
# RISE COURSE BUILD PLAN

Lesson Title:
{title}

Estimated Reading Time:
{round(wc / 180, 1)} minutes

Word Count:
{wc}

--------------------------------------------------

## Lesson Structure

1. Cover Page
   - Title
   - Subtitle
   - Visual banner

2. Introduction
   - Why this topic matters
   - Context setting

3. Core Lesson
   - Major concept blocks
   - Step-by-step explanation
   - Real-world examples

4. Knowledge Check

5. Scenario Activity

6. Reflection Exercise

7. Summary

--------------------------------------------------

## Recommended Rise Blocks

• Text
• Labeled Graphic
• Process Block
• Flashcards
• Scenario
• Knowledge Check
• Continue Divider

--------------------------------------------------

## Instructor Notes

Encourage discussion around:

• real world examples
• civic participation
• policy implications

Students should leave this lesson with a clear understanding of the topic
and how it applies to real community issues.
"""


# --------------------------------------------------
# Interaction Builder
# --------------------------------------------------

def build_interactions(title):

    return f"""
# INTERACTION BANK

Lesson:
{title}

--------------------------------------------------

Knowledge Check 1

Question:
What is the central concept discussed in this lesson?

Options:
A) Option one
B) Option two
C) Option three
D) Option four

Correct Answer:
Instructor selects based on lesson emphasis.

--------------------------------------------------

Reflection Prompt

Ask learners:

• How does this issue affect your community?
• What role should citizens play in addressing it?

--------------------------------------------------

Scenario Activity

Scenario:

A community is facing a challenge related to this topic.

Ask students to decide:

• What action should leaders take?
• What action should citizens take?

Discuss possible outcomes.
"""


# --------------------------------------------------
# Quiz Bank
# --------------------------------------------------

def build_quiz_bank(title):

    questions = []

    for i in range(1, 11):

        questions.append(f"""
Question {i}

What concept from the lesson best applies here?

A) Example A
B) Example B
C) Example C
D) Example D
""")

    return f"""
# QUIZ QUESTION BANK

Lesson:
{title}

--------------------------------------------------

{"".join(questions)}
"""


# --------------------------------------------------
# Media Plan
# --------------------------------------------------

def build_media_plan(title):

    return f"""
# MEDIA PLAN

Lesson:
{title}

--------------------------------------------------

Hero Image

Suggested image:

• Arkansas community scene
• civic engagement
• local government

--------------------------------------------------

Supporting Graphics

• Process diagram
• Timeline
• Civic structure chart

--------------------------------------------------

Video Suggestions

Short video explaining the concept
(2-4 minutes)

--------------------------------------------------

Visual Metaphors

Use visuals showing:

• networks
• systems
• community interaction
"""


# --------------------------------------------------
# Main Export
# --------------------------------------------------

def main():

    if len(sys.argv) < 2:
        print("Usage: python scripts/export_rise_course.py request.json")
        sys.exit(1)

    request_path = Path(sys.argv[1])

    if not request_path.exists():
        print("Request file not found.")
        sys.exit(1)

    body = json.loads(request_path.read_text(encoding="utf-8"))

    course = body.get("course", "course")
    chapter = body.get("chapter", "chapter")
    segment = body.get("segment", "segment")

    content = body.get("content", "")
    instruction = body.get("instruction", "")

    title = f"{clean_title(course)} {clean_title(chapter)} {clean_title(segment)}"

    base_name = slug(title)

    ai_import = build_ai_import(title, content, instruction)
    rise_plan = build_rise_plan(title, content)
    interactions = build_interactions(title)
    quiz_bank = build_quiz_bank(title)
    media_plan = build_media_plan(title)

    files = {
        f"{base_name}_AI_IMPORT.txt": ai_import,
        f"{base_name}_BUILD_PLAN.md": rise_plan,
        f"{base_name}_INTERACTIONS.md": interactions,
        f"{base_name}_QUIZ_BANK.md": quiz_bank,
        f"{base_name}_MEDIA_PLAN.md": media_plan,
    }

    for name, data in files.items():

        out_path = EXPORT_DIR / name

        out_path.write_text(data.strip(), encoding="utf-8")

        print(f"Generated: {out_path}")

    print("\nRise export complete.")


if __name__ == "__main__":
    main()