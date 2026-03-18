from pathlib import Path
import sys
from datetime import datetime

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from engine.track_engine import TrackEngine  # noqa: E402
from engine.learning_runtime import LearningRuntime  # noqa: E402


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

    section("Building Arkansas Civics Track Engine")

    engine = TrackEngine(ROOT)
    runtime = LearningRuntime(ROOT)

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
        print("\nPlatform structure issues detected:\n")
        for issue in validation.get("issues", []):
            print(f"- {issue}")
        print()
        fail("Track engine build aborted because source structure is invalid")

    success("Platform structure validated")

    section("Generating Track Definitions")
    track_paths = engine.export_track_definitions()
    track_count = len(engine.build_track_definitions())
    success(f"Track definitions generated for {track_count} tracks")
    info(f"Output directory: {engine.kernel.exports_dir / 'tracks'}")

    section("Generating Learning Runtime Blueprint")
    runtime_paths = runtime.export_runtime_blueprint(engine.kernel.exports_dir / 'tracks')
    success("Learning runtime blueprint generated")

    print("\nGenerated files:")
    for path in [*track_paths, *runtime_paths]:
        print(path)

    duration = (datetime.now() - start).total_seconds()
    print("\n------------------------------------")
    print(" TRACK ENGINE BUILD COMPLETE ")
    print("------------------------------------\n")
    print("Generated outputs should appear in:\n")
    print("exports/tracks/\n")
    print(f"Build completed in {duration:.2f} seconds.\n")


if __name__ == "__main__":
    main()
