from __future__ import annotations

from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Any
import json


# ============================================================
# Core data models
# ============================================================

@dataclass
class Segment:
    name: str
    path: Path
    relative_path: str
    content: str
    suffix: str = ".md"
    line_count: int = 0
    is_markdown: bool = True

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["path"] = str(self.path)
        return data


@dataclass
class Chapter:
    name: str
    slug: str
    path: Path
    relative_path: str
    segments: list[Segment] = field(default_factory=list)
    chapter_yaml_path: Path | None = None
    articulate_path: Path | None = None
    simulations_path: Path | None = None

    @property
    def has_named_segments(self) -> bool:
        return any(not s.name.endswith("_segment") for s in self.segments)

    @property
    def segment_count(self) -> int:
        return len(self.segments)

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "slug": self.slug,
            "path": str(self.path),
            "relative_path": self.relative_path,
            "segment_count": self.segment_count,
            "has_named_segments": self.has_named_segments,
            "chapter_yaml_path": str(self.chapter_yaml_path) if self.chapter_yaml_path else None,
            "articulate_path": str(self.articulate_path) if self.articulate_path else None,
            "simulations_path": str(self.simulations_path) if self.simulations_path else None,
            "segments": [segment.to_dict() for segment in self.segments],
        }


@dataclass
class Course:
    name: str
    slug: str
    path: Path
    relative_path: str
    readme_path: Path | None = None
    chapters: list[Chapter] = field(default_factory=list)

    @property
    def chapter_count(self) -> int:
        return len(self.chapters)

    @property
    def segment_count(self) -> int:
        return sum(chapter.segment_count for chapter in self.chapters)

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "slug": self.slug,
            "path": str(self.path),
            "relative_path": self.relative_path,
            "readme_path": str(self.readme_path) if self.readme_path else None,
            "chapter_count": self.chapter_count,
            "segment_count": self.segment_count,
            "chapters": [chapter.to_dict() for chapter in self.chapters],
        }


# ============================================================
# Platform kernel
# ============================================================

class PlatformKernel:
    """
    Arkansas Civics Platform Kernel

    Responsibilities:
    - Define canonical project paths
    - Load content from the filesystem
    - Normalize course/chapter/segment structure
    - Enforce source-of-truth rules
    - Provide reusable helpers for scripts
    - Support future validation, exports, and database integration
    """

    def __init__(self, root: str | Path | None = None) -> None:
        if root is None:
            self.root = Path(__file__).resolve().parents[1]
        else:
            self.root = Path(root).resolve()

        self.content_dir = self.root / "content"
        self.courses_dir = self.content_dir / "courses"
        self.config_dir = self.root / "config"
        self.engine_dir = self.root / "engine"
        self.scripts_dir = self.root / "scripts"
        self.exports_dir = self.root / "exports"
        self.apps_dir = self.root / "apps"
        self.dashboard_dir = self.apps_dir / "editor-dashboard"
        self.dashboard_content_dir = self.dashboard_dir / "content"
        self.dashboard_manifest_path = self.dashboard_dir / "content-manifest.json"
        self.netlify_dir = self.root / "netlify"
        self.data_dir = self.root / "data"
        self.docs_dir = self.root / "docs"

    # ========================================================
    # Path and system rules
    # ========================================================

    def assert_core_paths(self) -> None:
        required = [
            self.content_dir,
            self.courses_dir,
            self.scripts_dir,
            self.exports_dir,
            self.dashboard_dir,
        ]
        missing = [str(path) for path in required if not path.exists()]
        if missing:
            raise FileNotFoundError(
                "Arkansas Civics kernel could not find required paths:\n"
                + "\n".join(missing)
            )

    def get_source_of_truth_rules(self) -> dict[str, str]:
        return {
            "content": "authoritative source of truth",
            "apps/editor-dashboard/content": "generated mirror only",
            "exports": "generated outputs only",
            "archive": "inactive historical files only",
        }

    def is_source_content_path(self, path: str | Path) -> bool:
        path_obj = Path(path).resolve()
        try:
            path_obj.relative_to(self.content_dir.resolve())
            return True
        except ValueError:
            return False

    def is_dashboard_mirror_path(self, path: str | Path) -> bool:
        path_obj = Path(path).resolve()
        try:
            path_obj.relative_to(self.dashboard_content_dir.resolve())
            return True
        except ValueError:
            return False

    # ========================================================
    # Discovery helpers
    # ========================================================

    def discover_courses(self) -> list[Path]:
        self.assert_core_paths()
        if not self.courses_dir.exists():
            return []

        course_paths = [
            path for path in sorted(self.courses_dir.iterdir(), key=lambda p: p.name.lower())
            if path.is_dir() and path.name.startswith("course_")
        ]
        return course_paths

    def discover_chapters(self, course_path: Path) -> list[Path]:
        chapter_paths = [
            path for path in sorted(course_path.iterdir(), key=lambda p: p.name.lower())
            if path.is_dir() and path.name.startswith("chapter_")
        ]
        return chapter_paths

    def discover_segments(self, chapter_path: Path) -> list[Path]:
        segments_dir = chapter_path / "segments"
        if not segments_dir.exists():
            return []

        segment_paths = [
            path for path in sorted(segments_dir.iterdir(), key=lambda p: p.name.lower())
            if path.is_file() and path.suffix.lower() == ".md"
        ]
        return segment_paths

    # ========================================================
    # Loaders
    # ========================================================

    def load_segment(self, segment_path: Path) -> Segment:
        content = segment_path.read_text(encoding="utf-8", errors="ignore")
        return Segment(
            name=segment_path.stem,
            path=segment_path,
            relative_path=str(segment_path.relative_to(self.root)),
            content=content,
            suffix=segment_path.suffix.lower(),
            line_count=len(content.splitlines()),
            is_markdown=segment_path.suffix.lower() == ".md",
        )

    def load_chapter(self, chapter_path: Path) -> Chapter:
        segment_paths = self.discover_segments(chapter_path)
        segments = [self.load_segment(path) for path in segment_paths]

        chapter_yaml_path = chapter_path / "chapter.yaml"
        articulate_path = chapter_path / "articulate" if (chapter_path / "articulate").exists() else None
        simulations_path = chapter_path / "simulations" if (chapter_path / "simulations").exists() else None

        return Chapter(
            name=chapter_path.name,
            slug=chapter_path.name,
            path=chapter_path,
            relative_path=str(chapter_path.relative_to(self.root)),
            segments=segments,
            chapter_yaml_path=chapter_yaml_path if chapter_yaml_path.exists() else None,
            articulate_path=articulate_path,
            simulations_path=simulations_path,
        )

    def load_course(self, course_path: Path) -> Course:
        chapter_paths = self.discover_chapters(course_path)
        chapters = [self.load_chapter(path) for path in chapter_paths]

        readme_path = course_path / "README.md"

        return Course(
            name=course_path.name,
            slug=course_path.name,
            path=course_path,
            relative_path=str(course_path.relative_to(self.root)),
            readme_path=readme_path if readme_path.exists() else None,
            chapters=chapters,
        )

    def load_all_courses(self) -> list[Course]:
        return [self.load_course(course_path) for course_path in self.discover_courses()]

    # ========================================================
    # Dashboard mirror support
    # ========================================================

    def build_dashboard_manifest(self) -> dict[str, Any]:
        """
        Produces a normalized manifest based only on source content.
        The dashboard mirror should never be treated as authority.
        """
        courses = self.load_all_courses()

        manifest: dict[str, Any] = {
            "generated_from": "content/courses",
            "course_count": len(courses),
            "courses": [],
        }

        for course in courses:
            course_entry = {
                "name": course.name,
                "slug": course.slug,
                "path": course.relative_path,
                "chapter_count": course.chapter_count,
                "segment_count": course.segment_count,
                "chapters": [],
            }

            for chapter in course.chapters:
                chapter_entry = {
                    "name": chapter.name,
                    "slug": chapter.slug,
                    "path": chapter.relative_path,
                    "segment_count": chapter.segment_count,
                    "has_named_segments": chapter.has_named_segments,
                    "segments": [
                        {
                            "name": segment.name,
                            "path": segment.relative_path,
                            "line_count": segment.line_count,
                        }
                        for segment in chapter.segments
                    ],
                }
                course_entry["chapters"].append(chapter_entry)

            manifest["courses"].append(course_entry)

        return manifest

    def write_dashboard_manifest(self) -> Path:
        manifest = self.build_dashboard_manifest()
        self.dashboard_dir.mkdir(parents=True, exist_ok=True)
        self.dashboard_manifest_path.write_text(
            json.dumps(manifest, indent=2),
            encoding="utf-8",
        )
        return self.dashboard_manifest_path

    # ========================================================
    # Export support
    # ========================================================

    def ensure_export_dir(self, *parts: str) -> Path:
        target = self.exports_dir.joinpath(*parts)
        target.mkdir(parents=True, exist_ok=True)
        return target

    def export_system_snapshot(self, output_name: str = "platform_kernel_snapshot.json") -> Path:
        courses = self.load_all_courses()
        payload = {
            "project_root": str(self.root),
            "rules": self.get_source_of_truth_rules(),
            "course_count": len(courses),
            "courses": [course.to_dict() for course in courses],
        }

        output_dir = self.ensure_export_dir("system_map")
        output_path = output_dir / output_name
        output_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        return output_path

    # ========================================================
    # Validation support
    # ========================================================

    def validate_structure(self) -> dict[str, Any]:
        courses = self.load_all_courses()

        results: dict[str, Any] = {
            "ok": True,
            "issues": [],
            "summary": {
                "course_count": len(courses),
                "chapter_count": sum(course.chapter_count for course in courses),
                "segment_count": sum(course.segment_count for course in courses),
            },
        }

        if not courses:
            results["ok"] = False
            results["issues"].append("No courses found in content/courses.")

        for course in courses:
            if not course.chapters:
                results["ok"] = False
                results["issues"].append(f"{course.relative_path} has no chapters.")

            for chapter in course.chapters:
                if not chapter.segments:
                    results["ok"] = False
                    results["issues"].append(f"{chapter.relative_path} has no segments.")

        return results

    # ========================================================
    # Future database bridge
    # ========================================================

    def get_database_readiness_summary(self) -> dict[str, Any]:
        """
        Database is not active yet. This method exists so the rest of
        the platform can ask the kernel about persistence state later.
        """
        return {
            "database_connected": False,
            "database_type": None,
            "source_of_truth": "filesystem",
            "future_role": [
                "user progress tracking",
                "dashboard multi-user state",
                "analytics",
                "search indexing",
                "operational cache",
            ],
        }


def create_kernel(root: str | Path | None = None) -> PlatformKernel:
    return PlatformKernel(root=root)


if __name__ == "__main__":
    kernel = create_kernel()
    kernel.assert_core_paths()

    validation = kernel.validate_structure()
    manifest_path = kernel.write_dashboard_manifest()
    snapshot_path = kernel.export_system_snapshot()

    print("\n================================================")
    print(" Arkansas Civics Platform Kernel")
    print("================================================\n")
    print(f"Project root: {kernel.root}")
    print(f"Dashboard manifest written: {manifest_path}")
    print(f"System snapshot written: {snapshot_path}")
    print("\nValidation summary:")
    print(json.dumps(validation, indent=2))
    print("\nDatabase readiness:")
    print(json.dumps(kernel.get_database_readiness_summary(), indent=2))