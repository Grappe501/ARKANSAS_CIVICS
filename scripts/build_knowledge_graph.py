from __future__ import annotations

from datetime import datetime
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from engine.knowledge_graph_engine import KnowledgeGraphEngine  # noqa: E402


def section(title: str) -> None:
    print("\n================================================")
    print(f" {title}")
    print("================================================\n")


def main() -> None:
    start = datetime.now()
    section("Building Arkansas Civics Knowledge Graph")

    engine = KnowledgeGraphEngine(ROOT)
    engine.kernel.assert_core_paths()
    validation = engine.kernel.validate_structure()
    summary = validation.get("summary", {})

    print("Structure summary:")
    print(f"  Courses:  {summary.get('course_count', 0)}")
    print(f"  Chapters: {summary.get('chapter_count', 0)}")
    print(f"  Segments: {summary.get('segment_count', 0)}")

    if not validation.get("ok", False):
        print("\nPlatform structure issues detected:\n")
        for issue in validation.get("issues", []):
            print(f"- {issue}")
        sys.exit(1)

    paths = engine.export_graph()
    graph = engine.build_graph()

    section("Knowledge Graph Outputs")
    print(f"Node count: {graph['summary']['node_count']}")
    print(f"Edge count: {graph['summary']['edge_count']}")
    print(f"Concepts:   {graph['summary']['concept_count']}")
    print(f"Tags:       {graph['summary']['tag_count']}")
    print("\nGenerated files:")
    for path in paths:
        print(path)

    duration = (datetime.now() - start).total_seconds()
    print("\n------------------------------------")
    print(" KNOWLEDGE GRAPH BUILD COMPLETE ")
    print("------------------------------------\n")
    print("Generated outputs should appear in:\n")
    print("exports/knowledge_graph/")
    print(f"\nBuild completed in {duration:.2f} seconds.\n")


if __name__ == "__main__":
    main()
