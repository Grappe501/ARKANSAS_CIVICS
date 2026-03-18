from pathlib import Path
import html
import re

try:
    import markdown as markdown_lib  # type: ignore
except ModuleNotFoundError:
    markdown_lib = None

ROOT = Path(__file__).resolve().parents[1]
CONTENT_DIR = ROOT / "content" / "courses"
EXPORT_DIR = ROOT / "exports" / "reader_site"

HTML_TEMPLATE = """
<html>
<head>
<meta charset="UTF-8">
<title>Arkansas Civics Reader</title>
<style>
body {{
    font-family: Arial, sans-serif;
    margin: 40px;
    max-width: 900px;
    line-height: 1.6;
}}
nav {{
    margin-bottom: 30px;
}}
nav a {{
    margin-right: 15px;
}}
.segment {{
    margin-bottom: 60px;
}}
</style>
</head>
<body>
<h1>Arkansas Civics Project</h1>
<nav>
{nav_links}
</nav>
{content}
</body>
</html>
"""


def load_segments() -> dict[str, dict[str, list[Path]]]:
    courses: dict[str, dict[str, list[Path]]] = {}
    for course in sorted(CONTENT_DIR.iterdir()):
        if not course.is_dir():
            continue
        course_name = course.name
        courses[course_name] = {}
        for chapter in sorted(course.iterdir()):
            if not chapter.is_dir():
                continue
            segments_dir = chapter / "segments"
            if not segments_dir.exists():
                continue
            courses[course_name][chapter.name] = sorted(segments_dir.glob("*.md"))
    return courses


def simple_markdown_to_html(text: str) -> str:
    lines = text.splitlines()
    parts: list[str] = []
    paragraph: list[str] = []

    def flush_paragraph() -> None:
        nonlocal paragraph
        if paragraph:
            joined = " ".join(s.strip() for s in paragraph).strip()
            joined = html.escape(joined)
            joined = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", joined)
            joined = re.sub(r"\*(.+?)\*", r"<em>\1</em>", joined)
            parts.append(f"<p>{joined}</p>")
            paragraph = []

    for raw in lines:
        line = raw.rstrip()
        stripped = line.strip()
        if not stripped:
            flush_paragraph()
            continue
        if stripped.startswith("### "):
            flush_paragraph()
            parts.append(f"<h3>{html.escape(stripped[4:])}</h3>")
        elif stripped.startswith("## "):
            flush_paragraph()
            parts.append(f"<h2>{html.escape(stripped[3:])}</h2>")
        elif stripped.startswith("# "):
            flush_paragraph()
            parts.append(f"<h1>{html.escape(stripped[2:])}</h1>")
        elif stripped.startswith("- "):
            flush_paragraph()
            parts.append(f"<li>{html.escape(stripped[2:])}</li>")
        else:
            paragraph.append(stripped)

    flush_paragraph()

    # wrap consecutive li elements in ul
    final_parts: list[str] = []
    in_list = False
    for part in parts:
        if part.startswith("<li>"):
            if not in_list:
                final_parts.append("<ul>")
                in_list = True
            final_parts.append(part)
        else:
            if in_list:
                final_parts.append("</ul>")
                in_list = False
            final_parts.append(part)
    if in_list:
        final_parts.append("</ul>")
    return "\n".join(final_parts)


def convert_md_to_html(md_file: Path) -> str:
    text = md_file.read_text(encoding="utf-8")
    if markdown_lib is not None:
        return markdown_lib.markdown(text)
    return simple_markdown_to_html(text)


def generate_pages(courses: dict[str, dict[str, list[Path]]]) -> None:
    EXPORT_DIR.mkdir(parents=True, exist_ok=True)
    nav_links = []
    for course_name, chapters in courses.items():
        for chapter_name in chapters:
            page_name = f"{course_name}_{chapter_name}.html"
            nav_links.append(f'<a href="{page_name}">{course_name} {chapter_name}</a>')
    nav_html = "\n".join(nav_links)

    for course_name, chapters in courses.items():
        for chapter_name, segments in chapters.items():
            content_html = "".join(
                f'<div class="segment">{convert_md_to_html(seg)}</div>' for seg in segments
            )
            page_html = HTML_TEMPLATE.format(nav_links=nav_html, content=content_html)
            out_file = EXPORT_DIR / f"{course_name}_{chapter_name}.html"
            out_file.write_text(page_html, encoding="utf-8")

    print("\nReader site generated:")
    print(EXPORT_DIR)


def main() -> None:
    print("\nBuilding Reader Site...\n")
    generate_pages(load_segments())


if __name__ == "__main__":
    main()
