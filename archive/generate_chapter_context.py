from pathlib import Path
import sys
import yaml

ROOT = Path(__file__).resolve().parents[1]
CONTENT_DIR = ROOT / "content" / "courses"
OUTPUT_DIR = ROOT / "docs" / "chapter_context"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Import reusable library loader
sys.path.insert(0, str(ROOT))
from engine.library_loader import load_all_library, find_by_course


CHAPTER_HINTS = {
    "course_01_civic_awakening": {
        "chapter_01": {
            "title": "Pulling Up More Chairs",
            "topics": ["civic_engagement", "participation", "empty_rooms", "local_power"],
            "recommended_tags": ["initiative", "referendum", "power", "organizing_risk"]
        },
        "chapter_02": {
            "title": "How Power Actually Works",
            "topics": ["civic_power_map", "institutions", "direct_democracy", "local_government"],
            "recommended_tags": ["amendment_7", "at_large", "representation", "rcv"]
        },
        "chapter_03": {
            "title": "The Arkansas Civic Story",
            "topics": ["history", "labor", "racial_violence", "ballot_fights", "modern_awakening"],
            "recommended_tags": ["elaine", "tenant_farmers", "right_to_work", "LEARNS"]
        },
        "chapter_04": {
            "title": "The Tools Citizens Already Have",
            "topics": ["initiative", "referendum", "voting_systems", "organizing_tools"],
            "recommended_tags": ["amendment_7", "minimum_wage", "medical_marijuana", "at_large", "rcv"]
        },
    }
}


def flatten_library_items():
    data = load_all_library()
    items = []
    for _, group in data.items():
        items.extend(group)
    return items


def score_item(item, course_slug, chapter_slug):
    score = 0

    course_match = item.get("course_use", [])
    if course_slug in course_match:
        score += 5

    hints = CHAPTER_HINTS.get(course_slug, {}).get(chapter_slug, {})
    recommended_tags = set(hints.get("recommended_tags", []))
    item_tags = set(item.get("tags", []))
    score += len(recommended_tags.intersection(item_tags)) * 3

    item_topics = set(item.get("topics", []))
    hint_topics = set(hints.get("topics", []))
    score += len(item_topics.intersection(hint_topics)) * 2

    return score


def collect_context(course_slug, chapter_slug):
    items = flatten_library_items()

    ranked = []
    for item in items:
        s = score_item(item, course_slug, chapter_slug)
        if s > 0:
            ranked.append((s, item))

    ranked.sort(key=lambda x: x[0], reverse=True)
    return [item for _, item in ranked[:12]]


def chapter_segments(course_slug, chapter_slug):
    seg_dir = CONTENT_DIR / course_slug / chapter_slug / "segments"
    if not seg_dir.exists():
        return []

    return [p.name for p in sorted(seg_dir.glob("*.md"))]


def build_context_doc(course_slug, chapter_slug):
    hints = CHAPTER_HINTS.get(course_slug, {}).get(chapter_slug, {})
    selected_items = collect_context(course_slug, chapter_slug)
    segs = chapter_segments(course_slug, chapter_slug)

    chapter_title = hints.get("title", chapter_slug.replace("_", " ").title())

    lines = []
    lines.append(f"# Chapter Context: {chapter_title}\n")
    lines.append(f"**Course:** {course_slug}")
    lines.append(f"**Chapter:** {chapter_slug}\n")

    lines.append("## Writing Purpose\n")
    lines.append(
        "Use this file to ground the chapter in Arkansas history, direct democracy, civic power, "
        "movement strategy, and real stories before writing or revising segments.\n"
    )

    lines.append("## Segment Files\n")
    for seg in segs:
        lines.append(f"- {seg}")
    lines.append("")

    lines.append("## Suggested Chapter Topics\n")
    for topic in hints.get("topics", []):
        lines.append(f"- {topic}")
    lines.append("")

    lines.append("## Recommended Arkansas Examples\n")
    if not selected_items:
        lines.append("- No matching civic library items found yet.\n")
    else:
        for item in selected_items:
            title = item.get("title", "Untitled")
            year = item.get("year", "n/a")
            summary = item.get("summary", "")
            tags = ", ".join(item.get("tags", []))
            lines.append(f"### {title} ({year})")
            lines.append(f"{summary}")
            if tags:
                lines.append(f"- Tags: {tags}")
            if item.get("book_use"):
                lines.append(f"- Book use: {', '.join(item.get('book_use', []))}")
            if item.get("course_use"):
                lines.append(f"- Course use: {', '.join(item.get('course_use', []))}")
            lines.append("")

    lines.append("## Questions to Answer in Drafting\n")
    lines.append("- What emotional state should the reader enter this chapter with?")
    lines.append("- What Arkansas story makes the concept feel real?")
    lines.append("- What civic tool or institutional mechanism should the reader understand by the end?")
    lines.append("- What later chapters should this chapter quietly plant or foreshadow?")
    lines.append("- What workbook and workshop activities should align with this chapter?")
    lines.append("")

    lines.append("## Dashboard Research Prompts\n")
    lines.append("- Find Arkansas-specific stories that illustrate this chapter’s theme.")
    lines.append("- Pull demographic or county-level context where relevant.")
    lines.append("- Identify modern examples that mirror the historical pattern.")
    lines.append("- Suggest narrative bridges between personal story and civic structure.")
    lines.append("")

    return "\n".join(lines)


def main():
    if len(sys.argv) != 3:
        print("\nUsage:")
        print("python scripts/generate_chapter_context.py <course_slug> <chapter_slug>\n")
        print("Example:")
        print("python scripts/generate_chapter_context.py course_01_civic_awakening chapter_01\n")
        sys.exit(1)

    course_slug = sys.argv[1]
    chapter_slug = sys.argv[2]

    output = build_context_doc(course_slug, chapter_slug)
    out_file = OUTPUT_DIR / f"{course_slug}_{chapter_slug}_context.md"
    out_file.write_text(output, encoding="utf-8")

    print("\nChapter context generated:")
    print(out_file)
    print("")


if __name__ == "__main__":
    main()