from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

SEGMENTS_DIR = ROOT / "content" / "courses" / "course_01_civic_awakening" / "chapter_04" / "segments"


SEGMENTS = {

"01_segment.md": {
"title": "The Tools Citizens Already Have",
"tags": ["civic_tools", "citizen_power"],
"book_narrative": """By the time readers reach this chapter, one truth should be clear.

Democracy is not something that only happens every four years.

It is a system made up of tools.

Some of those tools belong to elected officials.

But many of them belong to citizens.

Arkansas voters possess the ability to organize communities, influence institutions, and in some cases even write laws directly.

The question is not whether those tools exist.

The question is whether people know how to use them.""",

"course_activity": "Learners identify civic tools they have personally used before.",
"workbook_exercise": "List three ways citizens can influence public decisions.",
"workshop_activity": "Group brainstorm: what tools do citizens actually possess?",
"facilitator_notes": "Introduce civic engagement as a toolkit."
},

"02_segment.md": {
"title": "Voting Is Only the Beginning",
"tags": ["voting", "participation"],
"book_narrative": """Voting is one of the most visible forms of civic participation.

But voting alone does not define democracy.

Between elections, thousands of decisions are made by institutions that respond to public pressure, advocacy, and organization.

Citizens who limit their participation to voting every few years often miss the spaces where influence actually happens.""",

"course_activity": "Learners identify civic actions that happen between elections.",
"workbook_exercise": "Write about a time when public pressure influenced a decision.",
"workshop_activity": "Discuss examples of community influence outside elections.",
"facilitator_notes": "Expand the reader’s understanding of participation."
},

"03_segment.md": {
"title": "Ballot Initiatives",
"tags": ["initiative", "direct_democracy"],
"book_narrative": """Arkansas is one of the states that allows citizens to propose laws directly through ballot initiatives.

This process allows voters to collect signatures and place an issue before the entire electorate.

Ballot initiatives have shaped many policies in Arkansas history.

From minimum wage increases to medical marijuana legalization, these campaigns demonstrate how organized citizens can bypass traditional political institutions.""",

"course_activity": "Learners review a past Arkansas ballot initiative.",
"workbook_exercise": "What issue might Arkansans attempt to place on the ballot?",
"workshop_activity": "Simulate the early planning of a ballot campaign.",
"facilitator_notes": "Explain initiative basics clearly."
},

"04_segment.md": {
"title": "Referendums",
"tags": ["referendum", "legislation"],
"book_narrative": """Referendums allow citizens to challenge laws passed by the legislature.

If enough signatures are gathered, a law can be placed on the ballot and voters can decide whether it should remain in place.

This process acts as a democratic check on legislative authority.""",

"course_activity": "Learners examine a referendum example.",
"workbook_exercise": "Write about why citizens might challenge a law.",
"workshop_activity": "Discuss when referendums might be appropriate.",
"facilitator_notes": "Introduce referendums as democratic accountability."
},

"05_segment.md": {
"title": "Petition Drives",
"tags": ["petition_drives", "grassroots"],
"book_narrative": """Petition drives are one of the most visible forms of grassroots organizing.

Volunteers travel across communities collecting signatures from voters.

Each signature represents a conversation about public policy.

Successful petition drives require organization, persistence, and broad community engagement.""",

"course_activity": "Learners explore how petition drives gather support.",
"workbook_exercise": "Describe the challenges of collecting signatures.",
"workshop_activity": "Practice approaching voters in a petition scenario.",
"facilitator_notes": "Emphasize relational organizing."
},

"06_segment.md": {
"title": "Voting Systems",
"tags": ["voting_systems", "representation"],
"book_narrative": """Not all voting systems operate the same way.

Different systems produce different political outcomes.

Some systems encourage majority representation.

Others allow minority voices greater influence.

Understanding voting systems helps citizens evaluate how democratic institutions function.""",

"course_activity": "Learners compare different voting systems.",
"workbook_exercise": "Which voting system seems most fair to you?",
"workshop_activity": "Simulate elections using different voting methods.",
"facilitator_notes": "Introduce institutional design."
},

"07_segment.md": {
"title": "At-Large Elections",
"tags": ["at_large", "representation"],
"book_narrative": """In some communities, officials are elected through at-large systems.

This means that all voters select candidates for every seat.

Historically, at-large systems were sometimes used to dilute minority representation.

Understanding these systems helps explain debates about fair representation.""",

"course_activity": "Learners examine an at-large election example.",
"workbook_exercise": "Write about how election systems affect representation.",
"workshop_activity": "Discuss fairness in electoral systems.",
"facilitator_notes": "Connect to civil rights history."
},

"08_segment.md": {
"title": "Ranked Choice Voting",
"tags": ["ranked_choice", "voting_reform"],
"book_narrative": """Ranked choice voting allows voters to rank candidates in order of preference.

If no candidate wins a majority, the lowest-ranked candidate is eliminated and votes are redistributed.

This system can encourage broader consensus and reduce the need for runoff elections.""",

"course_activity": "Learners participate in a ranked-choice election simulation.",
"workbook_exercise": "Describe advantages and disadvantages of ranked choice voting.",
"workshop_activity": "Group voting experiment.",
"facilitator_notes": "Keep explanation simple and visual."
},

"09_segment.md": {
"title": "Coalition Building",
"tags": ["coalitions", "movement_building"],
"book_narrative": """Successful civic campaigns rarely operate alone.

Coalitions bring together organizations, community leaders, and volunteers with shared goals.

These partnerships allow movements to expand their reach and legitimacy.""",

"course_activity": "Learners identify groups that might form a coalition.",
"workbook_exercise": "List organizations in your community that share similar concerns.",
"workshop_activity": "Build a hypothetical coalition map.",
"facilitator_notes": "Emphasize relationships over ideology."
},

"10_segment.md": {
"title": "Messaging and Public Narrative",
"tags": ["messaging", "communication"],
"book_narrative": """Movements succeed not only because of policy ideas but because of the stories they tell.

Public narratives shape how people understand problems and solutions.

Effective civic campaigns communicate clearly, emotionally, and consistently.""",

"course_activity": "Learners practice framing a civic message.",
"workbook_exercise": "Write a short message explaining an issue you care about.",
"workshop_activity": "Group messaging exercise.",
"facilitator_notes": "Introduce communication strategy."
},

"11_segment.md": {
"title": "From Tools to Action",
"tags": ["strategy", "organizing"],
"book_narrative": """The tools of democracy only matter when people use them.

Understanding voting systems, petition drives, and coalition building gives citizens the foundation to act.

Civic participation becomes powerful when knowledge turns into organization.""",

"course_activity": "Learners outline a civic strategy.",
"workbook_exercise": "What issue would you organize around?",
"workshop_activity": "Small group strategy planning.",
"facilitator_notes": "Transition from theory to action."
},

"12_segment.md": {
"title": "The Next Step",
"tags": ["transition", "future_action"],
"book_narrative": """This chapter introduced the tools citizens possess.

The chapters ahead will explore how movements form, grow, and confront opposition.

Understanding the tools is only the beginning.

Using them is where civic life truly begins.""",

"course_activity": "Preview the next course in the program.",
"workbook_exercise": "What civic tool are you most interested in learning more about?",
"workshop_activity": "Closing discussion about future engagement.",
"facilitator_notes": "Prepare readers for movement-building chapters."
}

}


TEMPLATE = """---
title: {title}
course: course_01_civic_awakening
chapter: chapter_04
segment: {segment}
tags:
{tags_block}
---

# {title}

## Book Narrative

{book_narrative}

## Course Activity

{course_activity}

## Workbook Exercise

{workbook_exercise}

## Workshop Activity

{workshop_activity}

## Facilitator Notes

{facilitator_notes}
"""


def format_tags(tags):
    return "\n".join([f"  - {tag}" for tag in tags])


def write_segments():

    SEGMENTS_DIR.mkdir(parents=True, exist_ok=True)

    for filename, data in SEGMENTS.items():

        out_path = SEGMENTS_DIR / filename

        content = TEMPLATE.format(
            title=data["title"],
            segment=filename.split("_")[0],
            tags_block=format_tags(data["tags"]),
            book_narrative=data["book_narrative"],
            course_activity=data["course_activity"],
            workbook_exercise=data["workbook_exercise"],
            workshop_activity=data["workshop_activity"],
            facilitator_notes=data["facilitator_notes"],
        )

        out_path.write_text(content, encoding="utf-8")

    print("\nChapter 4 seeded successfully.")
    print(f"Wrote {len(SEGMENTS)} segment files to:")
    print(SEGMENTS_DIR)


if __name__ == "__main__":
    write_segments()