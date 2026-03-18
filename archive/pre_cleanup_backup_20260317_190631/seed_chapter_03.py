from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

SEGMENTS_DIR = ROOT / "content" / "courses" / "course_01_civic_awakening" / "chapter_03" / "segments"


SEGMENTS = {

"01_segment.md": {
"title": "Arkansas Has Always Been a Civic Battleground",
"tags": ["arkansas_history", "civic_struggle"],
"book_narrative": """Arkansas has never been a quiet political place.

Beneath the surface of everyday life, the state has been shaped again and again by civic struggle.

Farmers organizing against railroad monopolies.

Sharecroppers demanding fair wages.

Civil rights activists challenging segregation.

Citizens gathering signatures to place laws directly on the ballot.

These moments did not always appear connected in their own time. But taken together they form a pattern.

Arkansas history is a story of ordinary people trying to shape systems that were not built with them in mind.""",

"course_activity": "Learners list three historical movements that shaped Arkansas politics.",
"workbook_exercise": "What movements or conflicts do you associate with Arkansas history?",
"workshop_activity": "Group brainstorm: what moments define Arkansas civic history?",
"facilitator_notes": "Open the chapter by framing history as civic struggle."
},

"02_segment.md": {
"title": "The Populist Era",
"tags": ["populism", "farmers", "political_reform"],
"book_narrative": """In the late nineteenth century, farmers across Arkansas faced enormous economic pressure.

Railroad monopolies controlled shipping.

Banks controlled credit.

Crop prices fluctuated wildly.

In response, farmers began organizing.

These movements helped fuel the rise of populist politics across the American South and Midwest.

The populist movement sought to give working people more influence over economic and political systems.""",

"course_activity": "Discuss why farmers became politically organized.",
"workbook_exercise": "What economic pressures push communities to organize today?",
"workshop_activity": "Compare populist concerns to modern economic debates.",
"facilitator_notes": "Show how economic struggles often drive political action."
},

"03_segment.md": {
"title": "The Promise and Limits of Reform",
"tags": ["reform", "democracy", "limitations"],
"book_narrative": """The populist movement promised to expand democratic participation.

But the South, including Arkansas, remained deeply shaped by racial divisions.

Many reform movements struggled with the tension between expanding economic democracy while confronting systems of racial exclusion.

These tensions would define much of Arkansas civic history in the decades that followed.""",

"course_activity": "Analyze tensions between reform and exclusion.",
"workbook_exercise": "Write about how reform movements sometimes contain contradictions.",
"workshop_activity": "Discuss why some movements expand democracy while others restrict it.",
"facilitator_notes": "Prepare readers for the Elaine Massacre segment."
},

"04_segment.md": {
"title": "The Elaine Massacre",
"tags": ["elaine_massacre", "racial_violence", "labor"],
"book_narrative": """In 1919, Black sharecroppers in Phillips County began organizing for fair payment for cotton crops.

They gathered in a church near Elaine, Arkansas to discuss forming a union.

The effort threatened the economic system that dominated the Delta.

Rumors spread that Black farmers were planning an uprising.

White mobs, joined by authorities and federal troops, responded with extraordinary violence.

Historians estimate that as many as two hundred Black Arkansans were killed.

The Elaine Massacre became one of the deadliest racial attacks in American history.""",

"course_activity": "Learners analyze why organizing sometimes provokes backlash.",
"workbook_exercise": "Reflect on why systems of power resist change.",
"workshop_activity": "Facilitated discussion about power and fear.",
"facilitator_notes": "Treat this section with seriousness and historical care."
},

"05_segment.md": {
"title": "The Supreme Court Case",
"tags": ["moore_v_dempsey", "civil_rights"],
"book_narrative": """After the violence in Elaine, several Black men were tried and sentenced to death in rushed trials.

Their case eventually reached the United States Supreme Court.

In Moore v. Dempsey (1923), the Court ruled that the trials had violated due process.

The decision became an important precedent for federal protection of civil rights.""",

"course_activity": "Learners examine the role of courts in protecting rights.",
"workbook_exercise": "Write about why judicial review matters.",
"workshop_activity": "Discuss how courts interact with democratic systems.",
"facilitator_notes": "Connect historical events to institutional structures."
},

"06_segment.md": {
"title": "The Southern Tenant Farmers Union",
"tags": ["tenant_farmers", "labor_organizing"],
"book_narrative": """In the 1930s, Arkansas again became a center of labor organizing.

The Southern Tenant Farmers Union formed in the Arkansas Delta.

The union brought together Black and white tenant farmers to demand fair treatment.

Their efforts challenged powerful landowners and exposed the harsh conditions of sharecropping.""",

"course_activity": "Discuss why cross-racial organizing was significant.",
"workbook_exercise": "Write about the challenges of building broad coalitions.",
"workshop_activity": "Group exercise: what makes coalitions succeed or fail?",
"facilitator_notes": "Highlight coalition-building across divisions."
},

"07_segment.md": {
"title": "Right-to-Work and Labor Politics",
"tags": ["right_to_work", "labor_policy"],
"book_narrative": """In 1944, Arkansas voters approved a constitutional amendment known as Right-to-Work.

The law restricted the ability of unions to require membership as a condition of employment.

Supporters argued it protected worker freedom.

Critics argued it weakened labor power.

The debate over collective bargaining and worker rights continues to shape Arkansas politics today.""",

"course_activity": "Learners debate arguments for and against right-to-work laws.",
"workbook_exercise": "What role should unions play in modern economies?",
"workshop_activity": "Structured debate exercise.",
"facilitator_notes": "Connect labor history to modern policy debates."
},

"08_segment.md": {
"title": "Civil Rights and Desegregation",
"tags": ["civil_rights", "desegregation"],
"book_narrative": """The mid-twentieth century brought new struggles over civil rights.

Arkansas became a focal point of the national desegregation battle during the Little Rock school crisis of 1957.

Students, activists, and national leaders confronted the question of whether the rule of law and constitutional rights would be upheld.""",

"course_activity": "Analyze the importance of the Little Rock desegregation crisis.",
"workbook_exercise": "Reflect on the role of courage in civic movements.",
"workshop_activity": "Discuss leadership during moments of civic conflict.",
"facilitator_notes": "Frame this moment as a national turning point."
},

"09_segment.md": {
"title": "The Rise of Ballot Initiatives",
"tags": ["initiative", "direct_democracy"],
"book_narrative": """Arkansas citizens possess a unique democratic tool: the ballot initiative.

Through Amendment 7, voters can propose laws or constitutional amendments directly to the public.

This process allows citizens to bypass the legislature and bring issues directly to the ballot.""",

"course_activity": "Learners review examples of successful Arkansas ballot initiatives.",
"workbook_exercise": "What issue would you consider placing on the ballot?",
"workshop_activity": "Petition drive simulation.",
"facilitator_notes": "Introduce direct democracy as a civic tool."
},

"10_segment.md": {
"title": "Modern Ballot Campaigns",
"tags": ["modern_ballot_initiatives"],
"book_narrative": """In recent decades, Arkansas voters have used the ballot initiative process to address issues ranging from minimum wage increases to medical marijuana legalization.

These campaigns required extensive grassroots organizing and statewide coalition building.""",

"course_activity": "Analyze how ballot campaigns gather signatures.",
"workbook_exercise": "Identify the steps needed to place an initiative on the ballot.",
"workshop_activity": "Group planning exercise for a hypothetical ballot campaign.",
"facilitator_notes": "Show the mechanics of organizing."
},

"11_segment.md": {
"title": "The Modern Civic Awakening",
"tags": ["learns_act", "petitions"],
"book_narrative": """In the 2020s, Arkansas experienced another surge of civic activity.

Efforts to challenge major legislation through referendums sparked organizing across the state.

Petition drives mobilized volunteers and engaged thousands of citizens in direct democratic action.""",

"course_activity": "Discuss modern civic engagement campaigns.",
"workbook_exercise": "Write about a recent Arkansas political event that drew public attention.",
"workshop_activity": "Share experiences of recent civic participation.",
"facilitator_notes": "Connect history to present-day activism."
},

"12_segment.md": {
"title": "What the Arkansas Story Teaches",
"tags": ["lessons", "history"],
"book_narrative": """The history of Arkansas civic life reveals a recurring pattern.

Communities organize.

Power responds.

Sometimes progress follows.

Sometimes backlash appears.

But each generation inherits the tools and lessons of those who came before.

Understanding that history prepares citizens to shape the next chapter.""",

"course_activity": "Learners identify key patterns in Arkansas civic history.",
"workbook_exercise": "What lesson from Arkansas history feels most important today?",
"workshop_activity": "Group reflection on historical patterns.",
"facilitator_notes": "Close the chapter by emphasizing continuity."
}

}


TEMPLATE = """---
title: {title}
course: course_01_civic_awakening
chapter: chapter_03
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

    print("\nChapter 3 seeded successfully.")
    print(f"Wrote {len(SEGMENTS)} segment files to:")
    print(SEGMENTS_DIR)


if __name__ == "__main__":
    write_segments()