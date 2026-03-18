from pathlib import Path
import sys
from datetime import datetime

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from engine.civic_intelligence_map import CivicIntelligenceMapEngine  # noqa: E402


def section(title: str) -> None:
    print("\n================================================")
    print(f" {title}")
    print("================================================\n")


def success(message: str) -> None:
    print(f"✔ {message}")


def fail(message: str) -> None:
    print(f"\n❌ {message}\n")
    sys.exit(1)


def main() -> None:
    start = datetime.now()
    section("Building Arkansas Civics Civic Intelligence Map")

    engine = CivicIntelligenceMapEngine(ROOT)

    try:
        engine.kernel.assert_core_paths()
        success("Core platform paths detected")
    except FileNotFoundError as exc:
        fail(str(exc))

    validation = engine.kernel.validate_structure()
    summary = validation.get("summary", {})
    print("Structure summary:")
    print(f"  Courses:  {summary.get('course_count', 0)}")
    print(f"  Chapters: {summary.get('chapter_count', 0)}")
    print(f"  Segments: {summary.get('segment_count', 0)}")

    if not validation.get("ok", False):
        for issue in validation.get("issues", []):
            print(f"- {issue}")
        fail("Civic intelligence map build aborted because source structure is invalid")

    outputs = engine.export()
    success("Civic intelligence map generated")
    print("\nGenerated files:")
    for path in outputs:
        print(path)

    duration = (datetime.now() - start).total_seconds()
    print("\n------------------------------------")
    print(" CIVIC INTELLIGENCE MAP BUILD COMPLETE ")
    print("------------------------------------\n")
    print("Generated outputs should appear in:\n")
    print("exports/civic_intelligence_map/")
    print(f"\nBuild completed in {duration:.2f} seconds.\n")


if __name__ == "__main__":
    main()
