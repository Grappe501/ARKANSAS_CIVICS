from pathlib import Path
import sys
from datetime import datetime

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from engine.track_engine import TrackEngine  # noqa: E402
from engine.learning_analytics_engine import LearningAnalyticsEngine  # noqa: E402
from engine.user_identity_engine import UserIdentityEngine  # noqa: E402
from engine.civic_mentor_engine import CivicMentorEngine  # noqa: E402
from engine.civic_intelligence_system import CivicIntelligenceSystem  # noqa: E402
from engine.civic_intelligence_map import CivicIntelligenceMapEngine  # noqa: E402
from engine.knowledge_graph_engine import KnowledgeGraphEngine  # noqa: E402


def section(title: str) -> None:
    print("\n================================================")
    print(f" {title}")
    print("================================================\n")


def success(message: str) -> None:
    print(f"✔ {message}")


def info(message: str) -> None:
    print(f"ℹ {message}")


def fail(message: str) -> None:
    print(f"\n❌ {message}\n")
    sys.exit(1)


def main() -> None:
    start = datetime.now()
    section("Building Arkansas Civic Intelligence System")

    system = CivicIntelligenceSystem(ROOT)

    try:
        system.kernel.assert_core_paths()
        success("Core platform paths detected")
    except FileNotFoundError as exc:
        fail(str(exc))

    validation = system.kernel.validate_structure()
    summary = validation.get("summary", {})
    print("Structure summary:")
    print(f"  Courses:  {summary.get('course_count', 0)}")
    print(f"  Chapters: {summary.get('chapter_count', 0)}")
    print(f"  Segments: {summary.get('segment_count', 0)}")

    if not validation.get("ok", False):
        print("\nPlatform structure issues detected:\n")
        for issue in validation.get("issues", []):
            print(f"- {issue}")
        fail("Civic intelligence build aborted because source structure is invalid")

    success("Platform structure validated")

    section("Exporting Supporting Engines")
    CivicIntelligenceMapEngine(ROOT).export()
    success("Civic intelligence map exported")

    KnowledgeGraphEngine(ROOT).export_graph()
    success("Knowledge graph exported")

    TrackEngine(ROOT).export_track_definitions()
    success("Track definitions exported")

    LearningAnalyticsEngine(ROOT).export_admin_reports()
    success("Learning analytics exported")

    UserIdentityEngine(ROOT).build_platform_identity_index()
    success("Identity index exported")

    CivicMentorEngine(ROOT).build_platform_brief()
    success("Mentor platform brief exported")

    section("Exporting Unified Civic Intelligence Snapshot")
    outputs = system.export_system()
    success("Unified civic intelligence snapshot exported")

    print("\nGenerated files:")
    for path in outputs:
        print(path)

    duration = (datetime.now() - start).total_seconds()
    print("\n--------------------------------------------")
    print(" CIVIC INTELLIGENCE BUILD COMPLETE ")
    print("--------------------------------------------\n")
    print("Primary dashboard output:\n")
    print("exports/civic_intelligence/civic_intelligence_dashboard.json\n")
    print(f"Build completed in {duration:.2f} seconds.\n")


if __name__ == "__main__":
    main()
