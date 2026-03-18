from pathlib import Path
import sys
from datetime import datetime
import traceback

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from engine.platform_kernel import create_kernel  # noqa: E402
from engine.civic_knowledge_graph_expansion_engine import CivicKnowledgeGraphExpansionEngine  # noqa: E402


def section(title: str) -> None:
    print("\n================================================")
    print(f" {title}")
    print("================================================\n")


def ok(message: str) -> None:
    print(f"[OK] {message}")


def info(message: str) -> None:
    print(f"[INFO] {message}")


def fail(message: str) -> None:
    print(f"[ERROR] {message}")


def main() -> None:
    start = datetime.now()

    try:
        section("Phase 06 - Civic Knowledge Graph Expansion")
        kernel = create_kernel(ROOT)
        kernel.assert_core_paths()
        ok("Core platform paths detected")

        validation = kernel.validate_structure()
        summary = validation.get("summary", {})
        print("Structure summary:")
        print(f"  Courses:  {summary.get('course_count', 0)}")
        print(f"  Chapters: {summary.get('chapter_count', 0)}")
        print(f"  Segments: {summary.get('segment_count', 0)}")

        if not validation.get("ok", False):
            print("\nValidation issues:")
            for issue in validation.get("issues", []):
                print(f"- {issue}")
            raise SystemExit(1)

        ok("Platform structure validated")

        section("Exporting Graph Expansion")
        engine = CivicKnowledgeGraphExpansionEngine(ROOT)
        outputs = engine.export()
        ok("Graph expansion exported")

        print("\nGenerated files:")
        for path in outputs:
            print(path)

        duration = (datetime.now() - start).total_seconds()
        print("\n--------------------------------------------")
        print(" PHASE 06 GRAPH EXPANSION COMPLETE")
        print("--------------------------------------------\n")
        info(f"Build completed in {duration:.2f} seconds")

    except Exception:
        fail("Phase 06 build failed\n")
        traceback.print_exc()
        raise SystemExit(1)


if __name__ == "__main__":
    main()
