from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

CONTENT_DIR = ROOT / "content" / "courses"
PLAN_DIR = ROOT / "docs" / "course_plans"

PLAN_DIR.mkdir(parents=True, exist_ok=True)


COURSE_DESCRIPTIONS = {
    "civic_awakening": "Introduce the problem of civic disengagement and show how local participation shapes democracy.",
    "arkansas_civic_history": "Explore Arkansas organizing history including populism, labor, civil rights, and modern activism.",
    "direct_democracy": "Teach how ballot initiatives and referendums allow citizens to bypass legislatures.",
    "voting_systems": "Explain how different voting systems shape political representation.",
    "labor_and_collective_power": "Explore union history, right-to-work laws, and collective bargaining strategies.",
    "shared_pain": "Teach how social movements begin when communities recognize shared struggles.",
    "shared_purpose": "Show how movements transform frustration into coordinated goals.",
    "coalition_building": "Explain how diverse communities build alliances for change.",
    "messaging_and_media": "Teach narrative building and political communication strategies.",
    "strategy_and_campaigns": "Show how movements organize campaigns and ballot initiatives.",
    "opposition_and_pushback": "Explore how power structures respond to civic organizing.",
    "sustaining_movements": "Teach how movements maintain momentum over time."
}


CHAPTER_STRUCTURE = [
    "Foundational concept",
    "Arkansas historical example",
    "Practical civic tools",
    "Movement strategy application"
]


def generate_plan(course_folder):

    course_name = course_folder.name
    course_key = "_".join(course_name.split("_")[2:])

    description = COURSE_DESCRIPTIONS.get(course_key, "Course description TBD.")

    chapters = sorted(course_folder.glob("chapter_*"))

    text = f"# {course_name.replace('_',' ').title()} Course Plan\n\n"

    text += "## Course Purpose\n\n"
    text += description + "\n\n"

    text += "## Chapter Overview\n\n"

    for i, chapter in enumerate(chapters):

        title = CHAPTER_STRUCTURE[i] if i < len(CHAPTER_STRUCTURE) else "Additional Topic"

        text += f"### {chapter.name.replace('_',' ').title()}\n\n"

        text += f"Focus: {title}\n\n"

        text += "**Book Narrative Idea**\n\n"
        text += "- Describe the civic concept and why it matters in Arkansas.\n\n"

        text += "**Arkansas Story Example**\n\n"
        text += "- Insert historical case study (e.g., Elaine Massacre, labor movement, ballot initiative fights).\n\n"

        text += "**Course Simulation**\n\n"
        text += "- Create a decision scenario related to the topic.\n\n"

        text += "**Workbook Exercise**\n\n"
        text += "- Ask learners to apply the concept to their own community.\n\n"

        text += "**Workshop Activity**\n\n"
        text += "- Facilitate group discussion or movement planning exercise.\n\n"

    return text


def generate_all():

    courses = sorted(CONTENT_DIR.glob("course_*"))

    for course in courses:

        plan_text = generate_plan(course)

        output_file = PLAN_DIR / f"{course.name}_plan.md"

        with open(output_file, "w", encoding="utf-8") as f:
            f.write(plan_text)

        print(f"Generated plan: {output_file}")


if __name__ == "__main__":

    print("\nGenerating Course Planning Documents...\n")

    generate_all()

    print("\nCourse planning files generated in docs/course_plans/\n")