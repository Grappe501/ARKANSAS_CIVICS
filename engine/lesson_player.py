from __future__ import annotations

from pathlib import Path
from typing import Any
import json
import math
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from engine.platform_kernel import create_kernel  # noqa: E402
from engine.course_engine import CourseEngine  # noqa: E402
from engine.progress_engine import ProgressEngine  # noqa: E402


class LessonPlayerEngine:
    """
    Produces learner-facing lesson player assets directly from real course content.

    Output philosophy:
      - no fake demo data
      - every route points at a real course, chapter, and segment
      - runtime hooks are included for future database-backed progress
    """

    def __init__(self, root: str | Path | None = None) -> None:
        self.kernel = create_kernel(root)
        self.course_engine = CourseEngine(root)
        self.progress_engine = ProgressEngine(root)
        self.root = self.kernel.root

    def export_player_assets(self) -> list[Path]:
        output_dir = self.kernel.ensure_export_dir("lesson_player")
        packages = self.course_engine.build_all_course_packages()
        runtime_snapshot_path = self.progress_engine.export_runtime_snapshot("demo_learner")

        player_index = {
            "generated_by": "engine.lesson_player",
            "source_of_truth": "content/courses",
            "course_count": len(packages),
            "courses": [],
        }

        output_paths: list[Path] = [runtime_snapshot_path]

        for package in packages:
            course_entry = {
                "slug": package.slug,
                "title": package.title,
                "source_path": package.source_path,
                "lesson_count": package.lesson_count,
                "total_estimated_minutes": package.total_estimated_minutes,
                "lessons": [],
            }

            for lesson in package.lessons:
                lesson_entry = {
                    "slug": lesson.slug,
                    "title": lesson.title,
                    "chapter_path": lesson.chapter_path,
                    "estimated_minutes": lesson.estimated_minutes,
                    "objective_count": len(lesson.objectives),
                    "activity_count": len(lesson.activities),
                    "assessment_count": len(lesson.assessments),
                    "tags": lesson.tags,
                    "segments": [],
                }

                blocks = list(lesson.blocks)
                for index, block in enumerate(blocks):
                    prev_block = blocks[index - 1] if index > 0 else None
                    next_block = blocks[index + 1] if index < len(blocks) - 1 else None
                    segment_name = block.source_segment_name
                    segment_file = f"{segment_name}.md" if not segment_name.endswith('.md') else segment_name

                    course_slug, chapter_slug = self._course_and_chapter_from_path(lesson.chapter_path)
                    lesson_entry["segments"].append(
                        {
                            "segment_name": segment_name,
                            "segment_title": block.title,
                            "block_type": block.block_type,
                            "order": block.order,
                            "estimated_minutes": max(1, math.ceil(self._word_count(block.body) / 180)),
                            "dashboard_content_path": f"./content/{course_slug}/{chapter_slug}/segments/{segment_file}",
                            "source_content_path": f"content/courses/{course_slug}/{chapter_slug}/segments/{segment_file}",
                            "previous_segment": prev_block.source_segment_name if prev_block else None,
                            "next_segment": next_block.source_segment_name if next_block else None,
                            "summary": self._summarize(block.body),
                            "supports_runtime": True,
                            "supports_completion": True,
                        }
                    )

                course_entry["lessons"].append(lesson_entry)

            player_index["courses"].append(course_entry)

            course_dir = output_dir / package.slug
            course_dir.mkdir(parents=True, exist_ok=True)
            course_json_path = course_dir / "lesson_player_course.json"
            course_json_path.write_text(json.dumps(course_entry, indent=2), encoding="utf-8")
            output_paths.append(course_json_path)

        player_index_path = output_dir / "lesson_player_index.json"
        player_index_path.write_text(json.dumps(player_index, indent=2), encoding="utf-8")
        output_paths.append(player_index_path)

        guide_path = output_dir / "lesson_player_readme.md"
        guide_path.write_text(self._render_readme(player_index), encoding="utf-8")
        output_paths.append(guide_path)

        return output_paths

    def _course_and_chapter_from_path(self, chapter_path: str) -> tuple[str, str]:
        parts = Path(chapter_path).parts
        try:
            course_index = parts.index("courses") + 1
            return parts[course_index], parts[course_index + 1]
        except Exception:
            # Fallback for relative content path styles
            cleaned = [p for p in parts if p.startswith("course_") or p.startswith("chapter_")]
            if len(cleaned) >= 2:
                return cleaned[0], cleaned[1]
            return "unknown_course", "unknown_chapter"

    def _word_count(self, text: str) -> int:
        return len(re.findall(r"\b\w+\b", text or ""))

    def _summarize(self, text: str, limit: int = 220) -> str:
        text = re.sub(r"\s+", " ", (text or "").strip())
        if len(text) <= limit:
            return text
        return text[:limit].rsplit(" ", 1)[0] + "…"

    def _render_readme(self, index_payload: dict[str, Any]) -> str:
        lines = [
            "# Arkansas Civics Lesson Player",
            "",
            "This export is a learner-facing navigation layer built from the real course content.",
            "",
            f"- Courses: {index_payload.get('course_count', 0)}",
            f"- Source of truth: `{index_payload.get('source_of_truth', 'content/courses')}`",
            "",
            "## Included assets",
            "",
            "- `lesson_player_index.json` — global player navigation index",
            "- `<course>/lesson_player_course.json` — per-course lesson routes",
            "- `../learning_runtime/learning_runtime_snapshot.json` — runtime snapshot seed",
            "",
            "## Design intent",
            "",
            "- Use real course content only",
            "- Support active learning clocks",
            "- Support completion tracking",
            "- Support future learner accounts and database persistence",
            "",
        ]
        return "\n".join(lines).strip() + "\n"


def build_and_export_lesson_player(root: str | Path | None = None) -> list[Path]:
    engine = LessonPlayerEngine(root)
    return engine.export_player_assets()


if __name__ == "__main__":
    engine = LessonPlayerEngine()
    paths = engine.export_player_assets()
    print("\n================================================")
    print(" Arkansas Civics Lesson Player Engine")
    print("================================================\n")
    for path in paths:
        print(path)
    print()
