from __future__ import annotations

from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any
import json
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from engine.platform_kernel import create_kernel  # noqa: E402

try:
    from engine.course_engine import CourseEngine  # noqa: E402
except Exception:  # pragma: no cover
    CourseEngine = None

try:
    from engine.track_engine import TrackEngine  # noqa: E402
except Exception:  # pragma: no cover
    TrackEngine = None


@dataclass
class MapNode:
    id: str
    label: str
    node_type: str
    slug: str
    source_path: str | None = None
    parent_id: str | None = None
    level: int = 0
    metadata: dict[str, Any] | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class MapEdge:
    source: str
    target: str
    edge_type: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class CivicIntelligenceMapEngine:
    """
    Builds a graph model for the Arkansas Civics platform from real source content.

    Current graph layers:
    - tracks
    - courses
    - chapters
    - segments

    Future graph layers can include:
    - counties
    - districts
    - legislation
    - people / roles
    - assessments
    - learner progress
    """

    def __init__(self, root: str | Path | None = None) -> None:
        self.kernel = create_kernel(root)
        self.root = self.kernel.root
        self.course_engine = CourseEngine(root) if CourseEngine is not None else None
        self.track_engine = TrackEngine(root) if TrackEngine is not None else None

    def build_map(self) -> dict[str, Any]:
        self.kernel.assert_core_paths()
        courses = self.kernel.load_all_courses()

        nodes: list[MapNode] = []
        edges: list[MapEdge] = []
        node_ids: set[str] = set()

        def add_node(node: MapNode) -> None:
            if node.id in node_ids:
                return
            node_ids.add(node.id)
            nodes.append(node)

        tracks_payload = self._build_track_payload(courses)

        for track in tracks_payload:
            track_id = f"track:{track['slug']}"
            add_node(
                MapNode(
                    id=track_id,
                    label=track["title"],
                    node_type="track",
                    slug=track["slug"],
                    source_path=None,
                    parent_id=None,
                    level=0,
                    metadata={
                        "estimated_minutes": track.get("estimated_minutes", 0),
                        "course_count": len(track.get("course_slugs", [])),
                        "description": track.get("description", ""),
                    },
                )
            )

            for course_slug in track.get("course_slugs", []):
                edges.append(MapEdge(source=track_id, target=f"course:{course_slug}", edge_type="contains-course"))

        for course in courses:
            course_id = f"course:{course.slug}"
            add_node(
                MapNode(
                    id=course_id,
                    label=self._humanize(course.slug),
                    node_type="course",
                    slug=course.slug,
                    source_path=course.relative_path,
                    parent_id=None,
                    level=1,
                    metadata={
                        "chapter_count": course.chapter_count,
                        "segment_count": course.segment_count,
                    },
                )
            )

            for chapter in course.chapters:
                chapter_id = f"chapter:{course.slug}:{chapter.slug}"
                add_node(
                    MapNode(
                        id=chapter_id,
                        label=self._humanize(chapter.slug),
                        node_type="chapter",
                        slug=chapter.slug,
                        source_path=chapter.relative_path,
                        parent_id=course_id,
                        level=2,
                        metadata={
                            "segment_count": chapter.segment_count,
                            "has_named_segments": chapter.has_named_segments,
                        },
                    )
                )
                edges.append(MapEdge(source=course_id, target=chapter_id, edge_type="contains-chapter"))

                for segment in chapter.segments:
                    segment_id = f"segment:{course.slug}:{chapter.slug}:{segment.name}"
                    add_node(
                        MapNode(
                            id=segment_id,
                            label=self._humanize(segment.name),
                            node_type="segment",
                            slug=segment.name,
                            source_path=segment.relative_path,
                            parent_id=chapter_id,
                            level=3,
                            metadata={
                                "line_count": segment.line_count,
                                "is_markdown": segment.is_markdown,
                            },
                        )
                    )
                    edges.append(MapEdge(source=chapter_id, target=segment_id, edge_type="contains-segment"))

        return {
            "generated_by": "engine.civic_intelligence_map",
            "source_of_truth": "content/courses",
            "project_root": str(self.root),
            "summary": {
                "track_count": sum(1 for node in nodes if node.node_type == "track"),
                "course_count": sum(1 for node in nodes if node.node_type == "course"),
                "chapter_count": sum(1 for node in nodes if node.node_type == "chapter"),
                "segment_count": sum(1 for node in nodes if node.node_type == "segment"),
                "edge_count": len(edges),
            },
            "nodes": [node.to_dict() for node in nodes],
            "edges": [edge.to_dict() for edge in edges],
            "tracks": tracks_payload,
        }

    def export(self, output_dir: Path | None = None) -> list[Path]:
        payload = self.build_map()
        if output_dir is None:
            output_dir = self.kernel.ensure_export_dir("civic_intelligence_map")
        else:
            output_dir.mkdir(parents=True, exist_ok=True)

        json_path = output_dir / "civic_intelligence_map.json"
        json_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

        md_path = output_dir / "civic_intelligence_map.md"
        md_path.write_text(self._render_markdown(payload), encoding="utf-8")

        return [json_path, md_path]

    def _build_track_payload(self, courses: list[Any]) -> list[dict[str, Any]]:
        if self.track_engine is not None:
            try:
                if hasattr(self.track_engine, "build_all_tracks"):
                    built = self.track_engine.build_all_tracks()
                    payload: list[dict[str, Any]] = []
                    for track in built:
                        course_slugs = []
                        if hasattr(track, "course_slugs"):
                            course_slugs = list(getattr(track, "course_slugs"))
                        elif hasattr(track, "courses"):
                            course_slugs = [getattr(c, "slug", str(c)) for c in getattr(track, "courses")]
                        payload.append(
                            {
                                "slug": getattr(track, "slug", "track"),
                                "title": getattr(track, "title", self._humanize(getattr(track, "slug", "track"))),
                                "description": getattr(track, "description", ""),
                                "estimated_minutes": getattr(track, "estimated_minutes", 0),
                                "course_slugs": course_slugs,
                            }
                        )
                    if payload:
                        return payload
            except Exception:
                pass

        # Fallback: one auto-generated track per course plus a foundation path
        all_course_slugs = [course.slug for course in courses]
        payload = [
            {
                "slug": "stand-up-arkansas-foundations",
                "title": "Stand Up Arkansas Foundations",
                "description": "A foundation path generated from the real Arkansas Civics course library.",
                "estimated_minutes": len(all_course_slugs) * 60,
                "course_slugs": all_course_slugs,
            }
        ]
        for course in courses:
            payload.append(
                {
                    "slug": f"track-{course.slug}",
                    "title": f"{self._humanize(course.slug)} Path",
                    "description": f"A focused pathway for {self._humanize(course.slug)}.",
                    "estimated_minutes": max(15, course.segment_count * 4),
                    "course_slugs": [course.slug],
                }
            )
        return payload

    def _render_markdown(self, payload: dict[str, Any]) -> str:
        lines = ["# Arkansas Civics Civic Intelligence Map", ""]
        summary = payload.get("summary", {})
        lines.append(f"- Tracks: {summary.get('track_count', 0)}")
        lines.append(f"- Courses: {summary.get('course_count', 0)}")
        lines.append(f"- Chapters: {summary.get('chapter_count', 0)}")
        lines.append(f"- Segments: {summary.get('segment_count', 0)}")
        lines.append(f"- Edges: {summary.get('edge_count', 0)}")
        lines.append("")

        lines.append("## Tracks")
        lines.append("")
        for track in payload.get("tracks", []):
            lines.append(f"### {track.get('title', track.get('slug', 'Track'))}")
            if track.get("description"):
                lines.append(track["description"])
            course_slugs = track.get("course_slugs", [])
            lines.append(f"- Courses: {len(course_slugs)}")
            lines.append(f"- Estimated minutes: {track.get('estimated_minutes', 0)}")
            for slug in course_slugs[:20]:
                lines.append(f"  - {slug}")
            lines.append("")
        return "\n".join(lines).strip() + "\n"

    def _humanize(self, value: str) -> str:
        return (
            value.replace("course_", "")
            .replace("chapter_", "")
            .replace("_", " ")
            .strip()
            .title()
        )


if __name__ == "__main__":
    engine = CivicIntelligenceMapEngine()
    outputs = engine.export()
    print("\n================================================")
    print(" Arkansas Civics Civic Intelligence Map Engine")
    print("================================================\n")
    for path in outputs:
        print(path)
    print()
