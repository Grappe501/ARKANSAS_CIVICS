from __future__ import annotations

from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Any
import json
import re
import sys

# ------------------------------------------------
# Ensure project root is importable when run directly
# ------------------------------------------------

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from engine.platform_kernel import (  # noqa: E402
    Chapter,
    Course,
    Segment,
    create_kernel,
)


# ============================================================
# Course Engine data models
# ============================================================

@dataclass
class LearningObjective:
    text: str
    bloom_level: str = "understand"

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class Activity:
    activity_type: str
    title: str
    instructions: str
    source_segment_name: str
    estimated_minutes: int = 5
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class AssessmentItem:
    question_type: str
    prompt: str
    answer_guidance: str
    source_segment_name: str
    points: int = 1
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class LessonBlock:
    block_type: str
    title: str
    body: str
    source_segment_name: str
    order: int

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class Lesson:
    title: str
    slug: str
    chapter_name: str
    chapter_path: str
    estimated_minutes: int
    objectives: list[LearningObjective] = field(default_factory=list)
    blocks: list[LessonBlock] = field(default_factory=list)
    activities: list[Activity] = field(default_factory=list)
    assessments: list[AssessmentItem] = field(default_factory=list)
    tags: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "title": self.title,
            "slug": self.slug,
            "chapter_name": self.chapter_name,
            "chapter_path": self.chapter_path,
            "estimated_minutes": self.estimated_minutes,
            "objectives": [objective.to_dict() for objective in self.objectives],
            "blocks": [block.to_dict() for block in self.blocks],
            "activities": [activity.to_dict() for activity in self.activities],
            "assessments": [assessment.to_dict() for assessment in self.assessments],
            "tags": self.tags,
            "metadata": self.metadata,
        }


@dataclass
class CoursePackage:
    title: str
    slug: str
    source_path: str
    lessons: list[Lesson] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def lesson_count(self) -> int:
        return len(self.lessons)

    @property
    def total_estimated_minutes(self) -> int:
        return sum(lesson.estimated_minutes for lesson in self.lessons)

    def to_dict(self) -> dict[str, Any]:
        return {
            "title": self.title,
            "slug": self.slug,
            "source_path": self.source_path,
            "lesson_count": self.lesson_count,
            "total_estimated_minutes": self.total_estimated_minutes,
            "metadata": self.metadata,
            "lessons": [lesson.to_dict() for lesson in self.lessons],
        }


# ============================================================
# Course Engine
# ============================================================

class CourseEngine:
    """
    Arkansas Civics internal course engine.

    Purpose:
    - Transform source content into an internal learning model
    - Replace dependence on external authoring structures
    - Generate reusable lessons, blocks, activities, and assessments
    - Prepare for future LMS, tracking, and custom authoring UI

    Source of truth remains:
        content/courses

    This engine is a transformation layer, not a persistence layer.
    """

    def __init__(self, root: str | Path | None = None) -> None:
        self.kernel = create_kernel(root)
        self.root = self.kernel.root

    # --------------------------------------------------------
    # Public API
    # --------------------------------------------------------

    def build_all_course_packages(self) -> list[CoursePackage]:
        self.kernel.assert_core_paths()
        courses = self.kernel.load_all_courses()
        return [self.build_course_package(course) for course in courses]

    def build_course_package(self, course: Course) -> CoursePackage:
        lessons = [self.build_lesson(chapter) for chapter in course.chapters]

        metadata = {
            "generated_by": "engine.course_engine",
            "source_of_truth": "content/courses",
            "chapter_count": course.chapter_count,
            "segment_count": course.segment_count,
            "readme_path": str(course.readme_path) if course.readme_path else None,
        }

        return CoursePackage(
            title=self.humanize_slug(course.slug),
            slug=course.slug,
            source_path=course.relative_path,
            lessons=lessons,
            metadata=metadata,
        )

    def build_lesson(self, chapter: Chapter) -> Lesson:
        blocks = self.build_blocks(chapter)
        objectives = self.build_objectives(chapter)
        activities = self.build_activities(chapter)
        assessments = self.build_assessments(chapter)

        estimated_minutes = max(
            10,
            sum(max(1, self.estimate_minutes_from_text(block.body)) for block in blocks)
            + sum(activity.estimated_minutes for activity in activities),
        )

        tags = self.build_tags(chapter)

        metadata = {
            "has_named_segments": chapter.has_named_segments,
            "segment_count": chapter.segment_count,
            "chapter_yaml_path": str(chapter.chapter_yaml_path) if chapter.chapter_yaml_path else None,
            "articulate_path": str(chapter.articulate_path) if chapter.articulate_path else None,
            "simulations_path": str(chapter.simulations_path) if chapter.simulations_path else None,
        }

        return Lesson(
            title=self.humanize_slug(chapter.slug),
            slug=chapter.slug,
            chapter_name=chapter.name,
            chapter_path=chapter.relative_path,
            estimated_minutes=estimated_minutes,
            objectives=objectives,
            blocks=blocks,
            activities=activities,
            assessments=assessments,
            tags=tags,
            metadata=metadata,
        )

    def export_course_packages(self, output_dir: Path | None = None) -> list[Path]:
        packages = self.build_all_course_packages()
        if output_dir is None:
            output_dir = self.kernel.ensure_export_dir("course_engine")

        output_paths: list[Path] = []

        for package in packages:
            course_dir = output_dir / package.slug
            course_dir.mkdir(parents=True, exist_ok=True)

            json_path = course_dir / "course_package.json"
            json_path.write_text(
                json.dumps(package.to_dict(), indent=2),
                encoding="utf-8",
            )
            output_paths.append(json_path)

            markdown_path = course_dir / "course_package.md"
            markdown_path.write_text(
                self.render_course_package_markdown(package),
                encoding="utf-8",
            )
            output_paths.append(markdown_path)

        index_path = output_dir / "course_engine_index.json"
        index_payload = {
            "generated_by": "engine.course_engine",
            "course_count": len(packages),
            "courses": [
                {
                    "slug": package.slug,
                    "title": package.title,
                    "lesson_count": package.lesson_count,
                    "total_estimated_minutes": package.total_estimated_minutes,
                }
                for package in packages
            ],
        }
        index_path.write_text(json.dumps(index_payload, indent=2), encoding="utf-8")
        output_paths.append(index_path)

        return output_paths

    # --------------------------------------------------------
    # Builders
    # --------------------------------------------------------

    def build_blocks(self, chapter: Chapter) -> list[LessonBlock]:
        blocks: list[LessonBlock] = []

        for index, segment in enumerate(chapter.segments, start=1):
            blocks.append(
                LessonBlock(
                    block_type=self.infer_block_type(segment),
                    title=self.humanize_slug(segment.name),
                    body=segment.content.strip(),
                    source_segment_name=segment.name,
                    order=index,
                )
            )

        return blocks

    def build_objectives(self, chapter: Chapter) -> list[LearningObjective]:
        objectives: list[LearningObjective] = []

        for segment in chapter.segments[:3]:
            phrase = self.first_meaningful_sentence(segment.content)
            if not phrase:
                continue

            objective_text = self.normalize_objective_text(
                f"Understand {self.humanize_slug(segment.name)} through Arkansas civic context."
            )
            objectives.append(
                LearningObjective(
                    text=objective_text,
                    bloom_level=self.infer_bloom_level(segment.name),
                )
            )

        if not objectives:
            objectives.append(
                LearningObjective(
                    text=f"Understand the key ideas in {self.humanize_slug(chapter.slug)}.",
                    bloom_level="understand",
                )
            )

        return objectives

    def build_activities(self, chapter: Chapter) -> list[Activity]:
        activities: list[Activity] = []

        for segment in chapter.segments:
            segment_label = self.humanize_slug(segment.name)
            segment_type = self.infer_block_type(segment)

            if "case_study" in segment.name:
                activities.append(
                    Activity(
                        activity_type="case-study",
                        title=f"Discuss: {segment_label}",
                        instructions=(
                            "Review the case study, identify the power dynamics involved, "
                            "and explain how the Arkansas example changes your understanding."
                        ),
                        source_segment_name=segment.name,
                        estimated_minutes=10,
                    )
                )
            elif "simulation" in segment.name:
                activities.append(
                    Activity(
                        activity_type="simulation",
                        title=f"Simulation: {segment_label}",
                        instructions=(
                            "Run a practical scenario based on this segment. Make a decision, "
                            "predict likely pushback, and outline your next three moves."
                        ),
                        source_segment_name=segment.name,
                        estimated_minutes=12,
                    )
                )
            elif segment_type == "reflection":
                activities.append(
                    Activity(
                        activity_type="reflection",
                        title=f"Reflect: {segment_label}",
                        instructions=(
                            "Write a short reflection connecting this topic to a real Arkansas "
                            "institution, campaign, or civic experience."
                        ),
                        source_segment_name=segment.name,
                        estimated_minutes=6,
                    )
                )

        if not activities:
            activities.append(
                Activity(
                    activity_type="discussion",
                    title=f"Discussion: {self.humanize_slug(chapter.slug)}",
                    instructions=(
                        "Discuss the chapter’s core civic lesson and identify one concrete "
                        "organizing application in Arkansas."
                    ),
                    source_segment_name=chapter.segments[0].name if chapter.segments else "chapter",
                    estimated_minutes=8,
                )
            )

        return activities

    def build_assessments(self, chapter: Chapter) -> list[AssessmentItem]:
        assessments: list[AssessmentItem] = []

        for segment in chapter.segments[:3]:
            assessments.append(
                AssessmentItem(
                    question_type="short-response",
                    prompt=(
                        f"What is the main civic lesson from '{self.humanize_slug(segment.name)}' "
                        "and why does it matter in Arkansas?"
                    ),
                    answer_guidance=(
                        "A strong answer should identify the core concept, explain its public impact, "
                        "and connect it to Arkansas institutions, history, or organizing strategy."
                    ),
                    source_segment_name=segment.name,
                    points=2,
                )
            )

        if chapter.segments:
            assessments.append(
                AssessmentItem(
                    question_type="application",
                    prompt=(
                        f"Using the lesson '{self.humanize_slug(chapter.slug)}', describe one "
                        "practical action a reader could take in a campaign, church, union, or ballot effort."
                    ),
                    answer_guidance=(
                        "A strong answer should move from theory to action and describe a real-world "
                        "step that could be taken in Arkansas."
                    ),
                    source_segment_name=chapter.segments[0].name,
                    points=3,
                )
            )

        return assessments

    def build_tags(self, chapter: Chapter) -> list[str]:
        tags = {"arkansas-civics", "lesson"}

        for segment in chapter.segments:
            name = segment.name.lower()

            if "history" in name or "historical" in name:
                tags.add("history")
            if "data" in name or "demographics" in name:
                tags.add("data")
            if "case_study" in name:
                tags.add("case-study")
            if "simulation" in name:
                tags.add("simulation")
            if "workshop" in name:
                tags.add("workshop")
            if "reader" in name:
                tags.add("reader")
            if "articulate" in name:
                tags.add("authoring")

        return sorted(tags)

    # --------------------------------------------------------
    # Rendering
    # --------------------------------------------------------

    def render_course_package_markdown(self, package: CoursePackage) -> str:
        lines: list[str] = []

        lines.append(f"# {package.title}")
        lines.append("")
        lines.append(f"- Slug: `{package.slug}`")
        lines.append(f"- Source: `{package.source_path}`")
        lines.append(f"- Lessons: {package.lesson_count}")
        lines.append(f"- Estimated minutes: {package.total_estimated_minutes}")
        lines.append("")

        for lesson in package.lessons:
            lines.append(f"## {lesson.title}")
            lines.append("")
            lines.append(f"- Chapter path: `{lesson.chapter_path}`")
            lines.append(f"- Estimated minutes: {lesson.estimated_minutes}")
            lines.append(f"- Tags: {', '.join(lesson.tags)}")
            lines.append("")

            lines.append("### Objectives")
            lines.append("")
            for objective in lesson.objectives:
                lines.append(f"- {objective.text} ({objective.bloom_level})")
            lines.append("")

            lines.append("### Content Blocks")
            lines.append("")
            for block in lesson.blocks:
                lines.append(f"#### {block.order}. {block.title}")
                lines.append("")
                lines.append(block.body[:1200].strip() if block.body else "")
                lines.append("")
                lines.append(f"_Block type: {block.block_type}_")
                lines.append("")

            lines.append("### Activities")
            lines.append("")
            for activity in lesson.activities:
                lines.append(f"- **{activity.title}** [{activity.activity_type}]")
                lines.append(f"  - Minutes: {activity.estimated_minutes}")
                lines.append(f"  - Instructions: {activity.instructions}")
            lines.append("")

            lines.append("### Assessments")
            lines.append("")
            for item in lesson.assessments:
                lines.append(f"- **{item.question_type}**: {item.prompt}")
                lines.append(f"  - Guidance: {item.answer_guidance}")
                lines.append(f"  - Points: {item.points}")
            lines.append("")

        return "\n".join(lines).strip() + "\n"

    # --------------------------------------------------------
    # Helpers
    # --------------------------------------------------------

    def infer_block_type(self, segment: Segment) -> str:
        name = segment.name.lower()

        if "overview" in name:
            return "overview"
        if "reader_psychology" in name:
            return "framing"
        if "historical_context" in name:
            return "history"
        if "data_and_demographics" in name:
            return "data"
        if "framework_or_model" in name:
            return "framework"
        if "case_study" in name:
            return "case-study"
        if "simulation" in name:
            return "simulation"
        if "articulate" in name:
            return "authoring"
        if "web_reader" in name:
            return "reader-extension"
        if "workshop" in name:
            return "workshop"
        if "revision_notes" in name:
            return "notes"
        return "reflection" if "reader" in name else "content"

    def infer_bloom_level(self, segment_name: str) -> str:
        name = segment_name.lower()

        if "framework" in name or "model" in name:
            return "analyze"
        if "case_study" in name or "simulation" in name:
            return "apply"
        if "revision" in name:
            return "evaluate"
        return "understand"

    def humanize_slug(self, value: str) -> str:
        cleaned = value
        cleaned = re.sub(r"^course_\d+_", "", cleaned)
        cleaned = re.sub(r"^chapter_\d+_", "", cleaned)
        cleaned = re.sub(r"^chapter_\d+$", "", cleaned)
        cleaned = cleaned.replace("_", " ").strip()
        if not cleaned:
            cleaned = value.replace("_", " ").strip()
        return cleaned.title()

    def first_meaningful_sentence(self, text: str) -> str:
        cleaned = re.sub(r"\s+", " ", text).strip()
        if not cleaned:
            return ""
        parts = re.split(r"(?<=[.!?])\s+", cleaned)
        return parts[0].strip() if parts else ""

    def normalize_objective_text(self, text: str) -> str:
        text = text.strip()
        if not text.endswith("."):
            text += "."
        return text

    def estimate_minutes_from_text(self, text: str) -> int:
        word_count = len(re.findall(r"\b\w+\b", text))
        return max(1, round(word_count / 180))


# ============================================================
# Convenience entrypoints
# ============================================================

def build_and_export_course_engine(root: str | Path | None = None) -> list[Path]:
    engine = CourseEngine(root=root)
    return engine.export_course_packages()


if __name__ == "__main__":
    engine = CourseEngine()
    output_paths = engine.export_course_packages()

    print("\n================================================")
    print(" Arkansas Civics Course Engine")
    print("================================================\n")
    print(f"Project root: {engine.root}")
    print(f"Courses loaded: {len(engine.build_all_course_packages())}")
    print("\nOutputs:")
    for path in output_paths:
        print(path)
    print()