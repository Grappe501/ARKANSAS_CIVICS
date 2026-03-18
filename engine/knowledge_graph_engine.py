from __future__ import annotations

from collections import Counter
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any
import json
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from engine.platform_kernel import create_kernel  # noqa: E402

STOPWORDS = {
    "the", "and", "for", "with", "that", "this", "from", "into", "their", "there",
    "about", "through", "while", "where", "when", "what", "your", "you", "have", "has",
    "will", "would", "could", "should", "been", "being", "than", "then", "them", "they",
    "our", "out", "are", "was", "were", "why", "how", "use", "used", "using", "over",
    "under", "more", "most", "less", "some", "many", "each", "other", "also", "only",
    "real", "mode", "notes", "revision", "segment", "chapter", "course", "reader", "study",
    "overview", "context", "historical", "history", "data", "demographics", "framework", "model",
    "case", "hook", "blocks", "bridge", "web", "extension", "articulate", "simulation"
}


@dataclass
class GraphNode:
    id: str
    label: str
    node_type: str
    metadata: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class GraphEdge:
    source: str
    target: str
    relation: str
    weight: int = 1
    metadata: dict[str, Any] | None = None

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        if payload["metadata"] is None:
            payload["metadata"] = {}
        return payload


class KnowledgeGraphEngine:
    """
    Builds a civic knowledge graph from the real Arkansas Civics content tree.

    Design goals:
    - no fake demo data
    - use the actual course/chapter/segment structure
    - extract reusable concepts from segment names and segment text
    - create graph nodes for tracks, courses, chapters, segments, concepts, and tags
    - export a production-friendly JSON payload for the Civic Intelligence Map
    """

    def __init__(self, root: str | Path | None = None) -> None:
        self.kernel = create_kernel(root)
        self.root = self.kernel.root
        self.nodes: dict[str, GraphNode] = {}
        self.edges: list[GraphEdge] = []
        self._edge_keys: set[tuple[str, str, str]] = set()

    # ---------------------------------------------------------
    # Public API
    # ---------------------------------------------------------
    def build_graph(self) -> dict[str, Any]:
        self.kernel.assert_core_paths()
        validation = self.kernel.validate_structure()
        if not validation.get("ok", False):
            issues = "\n".join(validation.get("issues", []))
            raise ValueError(f"Cannot build knowledge graph. Invalid platform structure:\n{issues}")

        courses = self.kernel.load_all_courses()
        track_index = self._load_track_index()

        self._build_track_layer(track_index)
        self._build_course_layer(courses)

        tag_counts = Counter(node.metadata.get("tag") for node in self.nodes.values() if node.node_type == "tag")
        concept_counts = Counter(node.metadata.get("term") for node in self.nodes.values() if node.node_type == "concept")

        graph = {
            "generated_by": "engine.knowledge_graph_engine",
            "source_of_truth": "content/courses",
            "project_root": str(self.root),
            "summary": {
                "node_count": len(self.nodes),
                "edge_count": len(self.edges),
                "course_count": len(courses),
                "track_count": len(track_index.get("tracks", [])) if isinstance(track_index, dict) else 0,
                "concept_count": sum(1 for node in self.nodes.values() if node.node_type == "concept"),
                "tag_count": sum(1 for node in self.nodes.values() if node.node_type == "tag"),
                "top_concepts": concept_counts.most_common(25),
                "top_tags": tag_counts.most_common(25),
            },
            "nodes": [node.to_dict() for node in self.nodes.values()],
            "edges": [edge.to_dict() for edge in self.edges],
        }
        return graph

    def export_graph(self, output_dir: Path | None = None) -> list[Path]:
        graph = self.build_graph()
        if output_dir is None:
            output_dir = self.kernel.ensure_export_dir("knowledge_graph")
        output_dir.mkdir(parents=True, exist_ok=True)

        json_path = output_dir / "knowledge_graph.json"
        json_path.write_text(json.dumps(graph, indent=2), encoding="utf-8")

        md_path = output_dir / "knowledge_graph.md"
        md_path.write_text(self.render_markdown(graph), encoding="utf-8")

        return [json_path, md_path]

    def render_markdown(self, graph: dict[str, Any]) -> str:
        summary = graph.get("summary", {})
        lines = [
            "# Arkansas Civics Knowledge Graph",
            "",
            "This file is generated from the real platform content and engines.",
            "",
            "## Summary",
            "",
            f"- Node count: {summary.get('node_count', 0)}",
            f"- Edge count: {summary.get('edge_count', 0)}",
            f"- Courses: {summary.get('course_count', 0)}",
            f"- Tracks: {summary.get('track_count', 0)}",
            f"- Concepts: {summary.get('concept_count', 0)}",
            f"- Tags: {summary.get('tag_count', 0)}",
            "",
            "## Top Concepts",
            "",
        ]
        for term, count in summary.get("top_concepts", [])[:20]:
            lines.append(f"- {term}: {count}")
        lines.extend(["", "## Top Tags", ""])
        for term, count in summary.get("top_tags", [])[:20]:
            lines.append(f"- {term}: {count}")
        return "\n".join(lines).strip() + "\n"

    # ---------------------------------------------------------
    # Graph builders
    # ---------------------------------------------------------
    def _build_track_layer(self, track_index: dict[str, Any]) -> None:
        tracks = track_index.get("tracks", []) if isinstance(track_index, dict) else []
        for track in tracks:
            track_slug = track.get("slug") or self._slugify(track.get("title") or "track")
            track_node_id = f"track:{track_slug}"
            self._add_node(track_node_id, track.get("title") or self._humanize(track_slug), "track", {
                "slug": track_slug,
                "estimated_minutes": track.get("estimated_minutes"),
                "track_type": track.get("track_type"),
            })
            for course_slug in track.get("course_slugs", []) or []:
                course_node_id = f"course:{course_slug}"
                self._add_edge(track_node_id, course_node_id, "includes")

    def _build_course_layer(self, courses: list[Any]) -> None:
        for course in courses:
            course_id = f"course:{course.slug}"
            self._add_node(course_id, self._humanize(course.slug), "course", {
                "slug": course.slug,
                "path": course.relative_path,
                "chapter_count": course.chapter_count,
                "segment_count": course.segment_count,
            })

            for chapter in course.chapters:
                chapter_id = f"chapter:{course.slug}:{chapter.slug}"
                self._add_node(chapter_id, self._humanize(chapter.slug), "chapter", {
                    "slug": chapter.slug,
                    "path": chapter.relative_path,
                    "segment_count": chapter.segment_count,
                    "course_slug": course.slug,
                })
                self._add_edge(course_id, chapter_id, "contains")

                chapter_tags = self._extract_tags(chapter.slug)
                for tag in chapter_tags:
                    tag_id = f"tag:{tag}"
                    self._add_node(tag_id, self._humanize(tag), "tag", {"tag": tag})
                    self._add_edge(chapter_id, tag_id, "tagged_with")

                for segment in chapter.segments:
                    segment_id = f"segment:{course.slug}:{chapter.slug}:{segment.name}"
                    preview = self._clean_preview(segment.content)
                    self._add_node(segment_id, self._humanize(segment.name), "segment", {
                        "name": segment.name,
                        "path": segment.relative_path,
                        "line_count": segment.line_count,
                        "chapter_slug": chapter.slug,
                        "course_slug": course.slug,
                        "preview": preview,
                    })
                    self._add_edge(chapter_id, segment_id, "contains")

                    block_type = self._infer_segment_type(segment.name)
                    type_id = f"tag:block-{block_type}"
                    self._add_node(type_id, f"Block {self._humanize(block_type)}", "tag", {"tag": f"block-{block_type}"})
                    self._add_edge(segment_id, type_id, "typed_as")

                    tags = sorted(set(self._extract_tags(segment.name) + chapter_tags))
                    for tag in tags:
                        tag_id = f"tag:{tag}"
                        self._add_node(tag_id, self._humanize(tag), "tag", {"tag": tag})
                        self._add_edge(segment_id, tag_id, "tagged_with")

                    concepts = self._extract_concepts(segment.name, segment.content)
                    for concept in concepts:
                        concept_id = f"concept:{concept}"
                        self._add_node(concept_id, self._humanize(concept), "concept", {"term": concept})
                        self._add_edge(segment_id, concept_id, "teaches")
                        for tag in tags[:5]:
                            self._add_edge(concept_id, f"tag:{tag}", "associated_with")

    # ---------------------------------------------------------
    # Data loading helpers
    # ---------------------------------------------------------
    def _load_track_index(self) -> dict[str, Any]:
        candidates = [
            self.root / "exports" / "track_engine" / "track_engine_index.json",
            self.root / "exports" / "tracks" / "track_engine_index.json",
            self.root / "exports" / "tracks" / "track_index.json",
        ]
        for path in candidates:
            if path.exists():
                try:
                    return json.loads(path.read_text(encoding="utf-8"))
                except Exception:
                    return {"tracks": []}
        return {"tracks": []}

    # ---------------------------------------------------------
    # Node / edge helpers
    # ---------------------------------------------------------
    def _add_node(self, node_id: str, label: str, node_type: str, metadata: dict[str, Any]) -> None:
        if node_id not in self.nodes:
            self.nodes[node_id] = GraphNode(node_id, label, node_type, metadata)

    def _add_edge(self, source: str, target: str, relation: str, weight: int = 1) -> None:
        key = (source, target, relation)
        if key in self._edge_keys:
            return
        self._edge_keys.add(key)
        self.edges.append(GraphEdge(source, target, relation, weight, {}))

    # ---------------------------------------------------------
    # Extraction helpers
    # ---------------------------------------------------------
    def _extract_tags(self, value: str) -> list[str]:
        text = value.lower()
        mapping = {
            "history": ["history", "historical", "reconstruction", "civil_rights", "elaine"],
            "organizing": ["organizing", "organizer", "campaign", "field", "coalition"],
            "leadership": ["leadership", "leader", "servant"],
            "messaging": ["message", "messaging", "media", "narrative"],
            "democracy": ["democracy", "ballot", "initiative", "referendum", "petition"],
            "voting": ["voting", "ranked_choice", "runoffs", "districts", "representation"],
            "labor": ["labor", "worker", "workers", "union", "bargaining"],
            "strategy": ["strategy", "pushback", "opposition", "rule_changes"],
            "ecosystem": ["ecosystem", "replication", "future", "platform"],
            "arkansas": ["arkansas"],
            "data": ["data", "demographics"],
            "simulation": ["simulation"],
            "case-study": ["case_study"],
        }
        tags = [tag for tag, needles in mapping.items() if any(needle in text for needle in needles)]
        return sorted(set(tags))

    def _extract_concepts(self, name: str, content: str) -> list[str]:
        concepts: set[str] = set()

        # concepts from segment name
        for token in self._tokenize(name.replace("_", " ")):
            if token not in STOPWORDS and len(token) > 2:
                concepts.add(token)

        # concepts from repeated meaningful words in content
        content_tokens = [token for token in self._tokenize(content) if token not in STOPWORDS and len(token) > 3]
        counts = Counter(content_tokens)
        for token, count in counts.most_common(12):
            if count >= 2:
                concepts.add(token)

        # concept phrases for common Arkansas civic patterns
        phrase_patterns = [
            r"arkansas constitution",
            r"direct democracy",
            r"civic engagement",
            r"shared pain",
            r"shared story",
            r"servant leadership",
            r"ballot initiatives?",
            r"collective bargaining",
            r"right to work",
            r"ranked choice",
            r"southern strategy",
            r"campaign manager",
            r"field operations",
            r"power mapping",
        ]
        lowered = content.lower()
        for pattern in phrase_patterns:
            for match in re.findall(pattern, lowered):
                concepts.add(self._slugify(match))

        return sorted(concepts)[:20]

    def _tokenize(self, text: str) -> list[str]:
        return [tok.lower() for tok in re.findall(r"[A-Za-z][A-Za-z_\-']+", text)]

    def _infer_segment_type(self, segment_name: str) -> str:
        name = segment_name.lower()
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
        if "workshop" in name:
            return "workshop"
        if "revision_notes" in name:
            return "notes"
        return "content"

    def _clean_preview(self, text: str, max_len: int = 240) -> str:
        cleaned = re.sub(r"\s+", " ", text).strip()
        if len(cleaned) <= max_len:
            return cleaned
        return cleaned[:max_len].rstrip() + "…"

    def _slugify(self, text: str) -> str:
        return re.sub(r"[^a-z0-9]+", "_", text.lower()).strip("_")

    def _humanize(self, value: str) -> str:
        value = re.sub(r"^course_\d+_", "", value)
        value = re.sub(r"^chapter_\d+_", "", value)
        value = value.replace("_", " ").strip()
        return value.title() if value else "Untitled"


def build_and_export_knowledge_graph(root: str | Path | None = None) -> list[Path]:
    engine = KnowledgeGraphEngine(root=root)
    return engine.export_graph()


if __name__ == "__main__":
    engine = KnowledgeGraphEngine()
    paths = engine.export_graph()
    print("\n================================================")
    print(" Arkansas Civics Knowledge Graph Engine")
    print("================================================\n")
    print(f"Project root: {engine.root}")
    print("Outputs:")
    for path in paths:
        print(path)
    print()
