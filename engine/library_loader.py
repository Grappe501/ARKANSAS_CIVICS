from pathlib import Path
import yaml

ROOT = Path(__file__).resolve().parents[1]
LIB = ROOT / "data" / "civic_library"


def load_yaml_folder(folder_name: str):
    folder = LIB / folder_name
    items = []

    if not folder.exists():
        return items

    for file in sorted(folder.glob("*.yaml")):
        with file.open("r", encoding="utf-8") as f:
            items.append(yaml.safe_load(f))

    return items


def load_all_library():
    data = {}
    for folder in [
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
    ]:
        data[folder] = load_yaml_folder(folder)
    return data


def find_by_tag(tag: str):
    results = []
    all_data = load_all_library()

    for _, items in all_data.items():
        for item in items:
            tags = item.get("tags", [])
            if tag in tags:
                results.append(item)

    return results


def find_by_course(course_slug: str):
    results = []
    all_data = load_all_library()

    for _, items in all_data.items():
        for item in items:
            course_use = item.get("course_use", [])
            if course_slug in course_use:
                results.append(item)

    return results