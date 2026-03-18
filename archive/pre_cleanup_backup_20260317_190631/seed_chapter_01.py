from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SEGMENTS_DIR = ROOT / "content" / "courses" / "course_01_civic_awakening" / "chapter_01" / "segments"

SEGMENTS = {
    "01_segment.md": {
        "title": "Opening Scene: A Tuesday Night Meeting",
        "tags": ["civic_engagement", "local_government", "opening_scene"],
        "book_narrative": """On a Tuesday evening in a small Arkansas town, the lights inside city hall come on long before anyone arrives.

The building itself is not remarkable. Brick walls, fluorescent lights, and a modest meeting room that has hosted decades of council meetings. A long table sits at the front where elected officials will soon gather. Microphones line the table, though in a room this small they are rarely necessary.

Rows of folding metal chairs fill the rest of the space.

Most nights, only a few of those chairs are occupied.

The meeting begins the same way it always does. The mayor calls the room to order. The clerk reads the agenda. Council members shuffle through printed packets of documents outlining the evening’s decisions.

Road repairs.

Zoning requests.

Budget adjustments.

Infrastructure projects.

These may sound like routine administrative tasks, but they are anything but trivial. Each item on that agenda represents a decision about how the community will function.

Where tax dollars will go.

How neighborhoods will grow.

What priorities the town will pursue.

Outside the building, life in the town continues uninterrupted.

Families eat dinner.

Students finish homework.

Restaurants close for the night.

Inside the meeting room, however, decisions are being made that will shape the community those families live in.

And yet most of the people who live there are not in the room.

The chairs remain empty.

And the meeting moves forward.""",
        "course_activity": "Scenario: The learner enters a small-town Arkansas public meeting and identifies the decisions being made in a room with very little public attendance.",
        "workbook_exercise": "Write down one public meeting in your town or county that most people never attend but that still shapes community life.",
        "workshop_activity": "Ask participants to describe a public room in their community where decisions are made but ordinary people are often absent.",
        "facilitator_notes": "Open with atmosphere and observation. The point is not policy yet; it is recognition."
    },

    "02_segment.md": {
        "title": "The Empty Room",
        "tags": ["empty_rooms", "participation", "recognition"],
        "book_narrative": """Scenes like this play out every week across Arkansas.

City councils meet.

County quorum courts gather.

School boards vote on policies that affect thousands of families.

The machinery of local government continues to operate exactly as it was designed.

But something has changed.

In many communities, the number of citizens participating in these meetings has steadily declined.

This decline did not happen suddenly. It unfolded slowly over decades, almost invisibly.

A generation ago, civic life looked different.

Community meetings were often social gatherings as much as political ones. Local leaders were members of civic clubs. Churches organized service projects. Parent-teacher organizations connected families to schools. Neighborhood groups formed around shared concerns.

These spaces acted as bridges between ordinary citizens and public decision-making.

Today, many of those bridges are weaker.""",
        "course_activity": "Learners compare two rooms: one empty and one full. They identify what changes when public presence changes.",
        "workbook_exercise": "List three spaces in your community where civic discussion used to happen more often than it does now.",
        "workshop_activity": "Have participants name local civic spaces that have gone quiet over time.",
        "facilitator_notes": "This section moves from scene to statewide pattern."
    },

    "03_segment.md": {
        "title": "The Quiet Civic Crisis",
        "tags": ["civic_crisis", "withdrawal", "arkansas"],
        "book_narrative": """Public conversations about community issues increasingly happen online — often in fragmented spaces that rarely translate into real-world collaboration.

Participation has shifted away from the places where decisions are actually made.

And when participation fades, something predictable happens.

Decision-making power concentrates among whoever remains in the room.

This is the quiet civic crisis.

It is not dramatic enough to dominate headlines every day. It does not always announce itself through scandal. Instead, it appears in thinning attendance, fading trust, and a growing sense among ordinary people that their presence will not matter.

The danger of this kind of crisis is that communities begin to accept it as normal.""",
        "course_activity": "Reflection: learners identify signs of civic decline in their own town.",
        "workbook_exercise": "Describe one way civic disengagement shows up in everyday life where you live.",
        "workshop_activity": "Group brainstorm: what does a quiet civic crisis look like locally?",
        "facilitator_notes": "Name the problem clearly. This gives the chapter its central tension."
    },

    "04_segment.md": {
        "title": "How Power Flows When Rooms Are Empty",
        "tags": ["power", "institutions", "absence"],
        "book_narrative": """When participation fades, power does not disappear.

It shifts.

When fewer citizens show up, leaders hear from fewer people. Organized interests, repeat players, and highly engaged factions naturally gain more influence. Even well-intentioned officials end up making decisions with a narrower set of perspectives in front of them.

The problem is not only corruption.

The problem is absence.

When communities are not present, the system keeps moving — but it moves with less democratic input.""",
        "course_activity": "Learners analyze how influence changes when citizens do not attend meetings.",
        "workbook_exercise": "Who keeps showing up in your local civic system when ordinary residents do not?",
        "workshop_activity": "Small group exercise: map who fills the gap when citizens withdraw.",
        "facilitator_notes": "Introduce power as relational and structural, not just partisan."
    },

    "05_segment.md": {
        "title": "An Arkansas Example of Local Power",
        "tags": ["arkansas_example", "city_council", "school_board", "quorum_court"],
        "book_narrative": """In Arkansas, local power is often more immediate than people realize.

A school board can change the trajectory of a district.

A city council can reshape development through zoning decisions.

A quorum court can direct county priorities through budgets and road funding.

These are not abstract powers. They affect classrooms, streets, businesses, and households.

Yet many Arkansans know the names of national political figures far better than the local officials whose decisions shape daily life.""",
        "course_activity": "Learners match Arkansas institutions to the kinds of decisions they control.",
        "workbook_exercise": "Name your city council member, school board member, quorum court justice, or county official if you can.",
        "workshop_activity": "Table exercise: identify one local institution that affects your life most directly.",
        "facilitator_notes": "Keep this grounded and practical."
    },

    "06_segment.md": {
        "title": "Why People Stopped Showing Up",
        "tags": ["disengagement", "trust", "fatigue"],
        "book_narrative": """People do not usually withdraw from civic life because they stop caring.

They withdraw because they become tired, frustrated, confused, or unconvinced that participation matters.

Some have attended meetings and felt ignored.

Some have watched public conversations become bitter and performative.

Some do not understand the systems well enough to feel comfortable entering them.

Others are simply carrying too much to give one more evening to a process that feels distant from their daily struggles.

The result is the same.

People stop showing up.""",
        "course_activity": "Learners sort common barriers to civic engagement into categories: trust, access, knowledge, time, conflict.",
        "workbook_exercise": "Which barrier most often keeps you or people you know from civic participation?",
        "workshop_activity": "Discussion circle: why do people in our community step back?",
        "facilitator_notes": "This is a crucial empathy segment."
    },

    "07_segment.md": {
        "title": "Arkansas Is Not Empty of Civic History",
        "tags": ["history_bridge", "arkansas_history", "transition"],
        "book_narrative": """Arkansas is not a state without civic traditions.

Its history is full of organizing, public struggle, and democratic conflict.

From populist movements and labor organizing to civil rights battles and ballot initiative campaigns, Arkansans have repeatedly shaped their future through collective action.

That history matters because it reminds us that civic life here did not vanish because Arkansans are incapable of participating.

It faded because habits changed, institutions hardened, and many people stopped believing the room belonged to them.

But what has faded can be rebuilt.""",
        "course_activity": "Transition exercise introducing Arkansas civic history as a source of possibility rather than nostalgia.",
        "workbook_exercise": "Write down one Arkansas movement or fight you want to learn more about.",
        "workshop_activity": "Facilitated preview of the Arkansas civic timeline.",
        "facilitator_notes": "This segment bridges Chapter 1 to later historical chapters."
    },

    "08_segment.md": {
        "title": "The First Hint of Direct Democracy",
        "tags": ["direct_democracy", "amendment_7", "citizen_power"],
        "book_narrative": """Arkansas citizens possess a power many Americans do not fully understand.

Through the ballot initiative and referendum process, voters can do more than choose representatives. They can place laws and constitutional changes directly before the people.

That matters because it means ordinary citizens in Arkansas are not limited to pleading with institutions.

Under certain conditions, they can act.

This is not an abstract theory. It has happened repeatedly in Arkansas history and will matter throughout this book.""",
        "course_activity": "Short explainer on what direct democracy means in Arkansas.",
        "workbook_exercise": "What issue in Arkansas might people try to place directly before voters?",
        "workshop_activity": "Quick pair discussion: why does direct democracy matter in a low-participation state?",
        "facilitator_notes": "Plant Amendment 7 here without fully teaching it yet."
    },

    "09_segment.md": {
        "title": "What an Empty Chair Means",
        "tags": ["symbol", "reader_reflection", "belonging"],
        "book_narrative": """An empty chair in a civic room is never just furniture.

It represents a voice that is absent.

A question that was never asked.

A story that was never told.

A priority that may never be heard.

When too many chairs stay empty for too long, a community slowly begins to lose the habit of hearing itself.

That is why the image matters.

The empty chair is not only a symbol of disengagement.

It is also an invitation.""",
        "course_activity": "Learners reflect on what is lost when people are absent from public life.",
        "workbook_exercise": "Who is missing most often from the rooms where decisions are made in your community?",
        "workshop_activity": "Place an empty chair in the room and ask participants to name who it represents.",
        "facilitator_notes": "Strong symbolic section. Good for workbook and live workshop crossover."
    },

    "10_segment.md": {
        "title": "The Reader Enters the Room",
        "tags": ["reader_insertion", "agency", "invitation"],
        "book_narrative": """At some point the question becomes personal.

If these rooms matter, where am I in relation to them?

Am I outside them entirely?

Am I watching from a distance?

Have I convinced myself they do not belong to me?

The shift toward civic awakening begins when a reader stops asking only what is wrong with the system and starts asking what it would mean to reenter it.""",
        "course_activity": "Prompt the learner to imagine attending a local meeting as a participant rather than observer.",
        "workbook_exercise": "What room in your community might you reenter first?",
        "workshop_activity": "Brief writing exercise: what would it take for me to show up?",
        "facilitator_notes": "Turn the chapter inward here."
    },

    "11_segment.md": {
        "title": "Pulling Up More Chairs",
        "tags": ["vision", "participation", "community"],
        "book_narrative": """Imagine that meeting room again.

The folding chairs are still there.

The agenda still lists routine items of local governance.

But tonight something is different.

Instead of empty seats, the room begins to fill.

Neighbors arrive.

Parents sit beside teachers.

Young people take seats near longtime residents who have attended these meetings for decades.

Conversations begin before the meeting even starts.

Questions are asked.

Ideas circulate.

The atmosphere shifts.

What was once a quiet procedural gathering becomes something else.

A civic space.

A place where citizens and leaders work together to shape the future of their community.

This transformation does not require extraordinary leadership.

It requires something simpler.

Citizens who are willing to participate.

Sometimes rebuilding civic life begins with a small act.

Sometimes it begins with simply pulling up more chairs.""",
        "course_activity": "Vision exercise: what changes when a room fills with real community presence?",
        "workbook_exercise": "Describe what a full civic room in your community would look and feel like.",
        "workshop_activity": "Group visualization exercise: from empty room to full room.",
        "facilitator_notes": "This is the hopeful turn of the chapter."
    },

    "12_segment.md": {
        "title": "Chapter 1 Bridge Forward",
        "tags": ["chapter_bridge", "foreshadowing", "course_transition"],
        "book_narrative": """This book begins with empty rooms, but it does not stay there.

The chapters ahead will ask harder questions.

How did Arkansas reach this point?

What tools do citizens still possess?

What does the state’s history of organizing teach us about power, backlash, and democratic possibility?

And what would it take, not just to talk about civic renewal, but to build it?

For now, the first step is enough.

Notice the room.

Notice the chairs.

And ask whether they are waiting for someone like you.""",
        "course_activity": "Preview the next three chapters and how they deepen the reader’s understanding of civic power.",
        "workbook_exercise": "What question are you carrying into the next chapter?",
        "workshop_activity": "Closing round: one word for how participants feel leaving Chapter 1.",
        "facilitator_notes": "Use this to bridge to Chapter 2."
    },
}


TEMPLATE = """---
title: {title}
course: course_01_civic_awakening
chapter: chapter_01
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

    print("\nChapter 1 seeded successfully.\n")
    print(f"Wrote {len(SEGMENTS)} segment files to:")
    print(SEGMENTS_DIR)
    print("")


if __name__ == "__main__":
    write_segments()