from pathlib import Path
import yaml

ROOT = Path(__file__).resolve().parents[1]
LIB = ROOT / "data" / "civic_library"

FOLDERS = [
    "stories",
    "events",
    "laws",
    "ballot_initiatives",
    "movements",
    "voting_systems",
    "counties",
    "demographics",
    "people",
    "institutions",
    "timelines",
]

SEED_FILES = {
    "events/1919_elaine_massacre.yaml": {
        "id": "event_elaine_1919",
        "title": "Elaine Massacre",
        "year": 1919,
        "era": "jim_crow",
        "location": ["Phillips County", "Elaine", "Arkansas Delta"],
        "topics": ["racial_violence", "labor", "organizing", "backlash"],
        "summary": "Black sharecroppers organizing for fair payment were met with mass racial violence in Phillips County.",
        "book_use": [
            "movement_formula",
            "opposition_and_pushback",
            "arkansas_civic_history"
        ],
        "course_use": [
            "course_02_arkansas_civic_history",
            "course_10_opposition_and_pushback"
        ],
        "workshop_use": [
            "historical warning case study"
        ],
        "tags": ["elaine", "sharecroppers", "power", "organizing_risk"]
    },

    "movements/1934_southern_tenant_farmers_union.yaml": {
        "id": "movement_stfu_1934",
        "title": "Southern Tenant Farmers' Union",
        "year": 1934,
        "era": "new_deal",
        "location": ["Tyronza", "Eastern Arkansas"],
        "topics": ["labor", "tenant_farmers", "cross_racial_organizing"],
        "summary": "Black and white tenant farmers organized together against exploitative agricultural conditions.",
        "book_use": [
            "shared_pain",
            "coalition_building",
            "labor_and_collective_power"
        ],
        "course_use": [
            "course_02_arkansas_civic_history",
            "course_05_labor_and_collective_power",
            "course_07_coalition_building"
        ],
        "tags": ["labor", "tenant_farmers", "coalition", "arkansas_delta"]
    },

    "laws/1944_right_to_work_amendment_34.yaml": {
        "id": "law_right_to_work_1944",
        "title": "Right-to-Work (Amendment 34)",
        "year": 1944,
        "era": "post_new_deal",
        "topics": ["labor", "right_to_work", "collective_bargaining"],
        "summary": "Arkansas adopted one of the earliest Right-to-Work constitutional provisions in the country.",
        "book_use": [
            "labor_and_collective_power",
            "direct_democracy",
            "tools_citizens_have"
        ],
        "course_use": [
            "course_03_direct_democracy",
            "course_05_labor_and_collective_power"
        ],
        "tags": ["right_to_work", "amendment_34", "labor_policy"]
    },

    "ballot_initiatives/1910_amendment_7_direct_democracy.yaml": {
        "id": "initiative_amendment_7_1910",
        "title": "Amendment 7: Initiative and Referendum",
        "year": 1910,
        "era": "progressive_era",
        "topics": ["direct_democracy", "initiative", "referendum"],
        "summary": "Arkansans adopted direct democracy tools allowing citizens to propose and refer laws.",
        "book_use": [
            "tools_citizens_have",
            "direct_democracy",
            "civic_power_map"
        ],
        "course_use": [
            "course_03_direct_democracy",
            "course_04_voting_systems",
            "course_09_strategy_and_campaigns"
        ],
        "tags": ["amendment_7", "initiative", "referendum"]
    },

    "ballot_initiatives/2014_minimum_wage_initiative.yaml": {
        "id": "initiative_minimum_wage_2014",
        "title": "2014 Minimum Wage Initiative",
        "year": 2014,
        "era": "modern",
        "topics": ["ballot_initiative", "economic_justice", "wages"],
        "summary": "Arkansas voters approved a citizen-led minimum wage increase.",
        "book_use": [
            "direct_democracy",
            "movement_examples"
        ],
        "course_use": [
            "course_03_direct_democracy",
            "course_09_strategy_and_campaigns"
        ],
        "tags": ["minimum_wage", "ballot", "economic_fairness"]
    },

    "ballot_initiatives/2016_medical_marijuana.yaml": {
        "id": "initiative_medical_marijuana_2016",
        "title": "2016 Medical Marijuana Initiative",
        "year": 2016,
        "era": "modern",
        "topics": ["ballot_initiative", "health_policy"],
        "summary": "Arkansas voters approved medical marijuana through the ballot initiative process.",
        "book_use": ["direct_democracy"],
        "course_use": [
            "course_03_direct_democracy",
            "course_09_strategy_and_campaigns"
        ],
        "tags": ["medical_marijuana", "initiative", "voters"]
    },

    "events/2023_learns_act_referendum_fight.yaml": {
        "id": "event_learns_referendum_2023",
        "title": "LEARNS Act Referendum Fight",
        "year": 2023,
        "era": "modern",
        "topics": ["education", "referendum", "grassroots_organizing"],
        "summary": "A statewide referendum effort attempted to place the LEARNS Act before voters, catalyzing broad civic engagement.",
        "book_use": [
            "modern_civic_awakening",
            "direct_democracy",
            "movement_formula"
        ],
        "course_use": [
            "course_03_direct_democracy",
            "course_09_strategy_and_campaigns",
            "course_10_opposition_and_pushback"
        ],
        "tags": ["LEARNS", "CAPES", "education", "referendum"]
    },

    "events/2024_2025_summer_of_petitions.yaml": {
        "id": "event_summer_of_petitions_2024_2025",
        "title": "Summer of Petitions / Civic Engagement Surge",
        "year": 2025,
        "era": "modern",
        "topics": ["petitions", "abortion", "education", "direct_democracy"],
        "summary": "Multiple petition drives across Arkansas helped create a statewide surge in civic participation and organizing.",
        "book_use": [
            "modern_civic_awakening",
            "movement_ladder",
            "direct_democracy"
        ],
        "course_use": [
            "course_09_strategy_and_campaigns",
            "course_10_opposition_and_pushback",
            "course_12_sustaining_movements"
        ],
        "tags": ["petitions", "summer_of_civic_engagement", "ballot_access"]
    },

    "events/2025_ballot_restrictions_backlash.yaml": {
        "id": "event_ballot_restrictions_2025",
        "title": "Legislative Backlash Against Ballot Access",
        "year": 2025,
        "era": "modern",
        "topics": ["ballot_access", "legislative_backlash", "rule_changes"],
        "summary": "Following petition-driven civic engagement, the General Assembly pursued multiple measures to limit direct democracy access.",
        "book_use": [
            "civic_engagement_cycle",
            "opposition_and_pushback"
        ],
        "course_use": [
            "course_10_opposition_and_pushback",
            "course_12_sustaining_movements"
        ],
        "tags": ["ballot_access", "rule_changes", "pushback"]
    },

    "voting_systems/at_large_voting.yaml": {
        "id": "voting_at_large",
        "title": "At-Large Voting",
        "system_type": "representation_system",
        "topics": ["voting_systems", "representation", "jim_crow"],
        "summary": "At-large systems can allow majority blocs to control all seats and historically diluted minority representation in the South.",
        "book_use": [
            "voting_systems",
            "jim_crow_history"
        ],
        "course_use": [
            "course_04_voting_systems"
        ],
        "tags": ["at_large", "jim_crow", "representation"]
    },

    "voting_systems/ranked_choice_voting.yaml": {
        "id": "voting_ranked_choice",
        "title": "Ranked Choice Voting",
        "system_type": "single_winner_and_multi_winner",
        "topics": ["voting_systems", "ranked_choice", "majority"],
        "summary": "Ranked choice voting lets voters rank candidates and can eliminate separate runoff elections.",
        "book_use": [
            "voting_systems",
            "tools_citizens_have"
        ],
        "course_use": [
            "course_04_voting_systems"
        ],
        "tags": ["rcv", "majority", "reform"]
    },

    "counties/arkansas_counties_index.yaml": {
        "id": "counties_index",
        "title": "Arkansas Counties Index",
        "summary": "Starter index for county-level expansion.",
        "counties": [
            "Pulaski", "Washington", "Benton", "Jefferson", "Craighead",
            "Sebastian", "Garland", "Faulkner", "Saline", "Phillips"
        ]
    },

    "timelines/arkansas_civic_engagement_timeline.yaml": {
        "id": "timeline_arkansas_civic_engagement",
        "title": "Arkansas Civic Engagement Timeline",
        "summary": "Master timeline for major civic and organizing moments.",
        "event_ids": [
            "initiative_amendment_7_1910",
            "event_elaine_1919",
            "movement_stfu_1934",
            "law_right_to_work_1944",
            "initiative_minimum_wage_2014",
            "initiative_medical_marijuana_2016",
            "event_learns_referendum_2023",
            "event_summer_of_petitions_2024_2025",
            "event_ballot_restrictions_2025"
        ]
    }
}


def write_yaml(path: Path, data: dict):
    path.parent.mkdir(parents=True, exist_ok=True)
    if not path.exists():
        with path.open("w", encoding="utf-8") as f:
            yaml.safe_dump(data, f, sort_keys=False, allow_unicode=True)


def build_library():
    LIB.mkdir(parents=True, exist_ok=True)

    for folder in FOLDERS:
        (LIB / folder).mkdir(parents=True, exist_ok=True)

    for rel_path, data in SEED_FILES.items():
        write_yaml(LIB / rel_path, data)

    readme = LIB / "README.md"
    if not readme.exists():
        readme.write_text(
            "# Arkansas Civic Content Library\n\n"
            "This library stores reusable Arkansas civic content for the book, course, workbook, workshop, facilitator guide, and website.\n\n"
            "Suggested future expansion:\n"
            "- county-level profiles\n"
            "- demographic snapshots\n"
            "- organizing story bank\n"
            "- election administration references\n"
            "- labor and union timeline\n"
            "- church and faith-based organizing examples\n",
            encoding="utf-8"
        )

    print("\nArkansas Civic Content Library created.\n")
    print(f"Root: {LIB}")


if __name__ == "__main__":
    build_library()