from pathlib import Path
import sys
from datetime import datetime

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from engine.lesson_player import LessonPlayerEngine  # noqa: E402


def section(title: str) -> None:
    print("\n================================================")
    print(f" {title}")
    print("================================================\n")


def success(message: str) -> None:
    print(f"✔ {message}")


def fail(message: str) -> None:
    print(f"\n❌ {message}\n")
    sys.exit(1)


def info(message: str) -> None:
    print(f"ℹ {message}")


def main() -> None:
    start = datetime.now()
    section("Building Arkansas Civics Lesson Player")

    engine = LessonPlayerEngine(ROOT)

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
        fail("Lesson player build aborted because source structure is invalid")

    success("Platform structure validated")

    section("Generating Lesson Player Assets")
    output_paths = engine.export_player_assets()
    success("Lesson player assets generated")
    info(f"Output directory: {engine.kernel.exports_dir / 'lesson_player'}")

    print("\nGenerated files:")
    for path in output_paths:
        print(path)

    duration = (datetime.now() - start).total_seconds()
    print("\n------------------------------------")
    print(" LESSON PLAYER BUILD COMPLETE ")
    print("------------------------------------\n")
    print("Generated outputs should appear in:\n")
    print("exports/lesson_player/")
    print("exports/learning_runtime/")
    print("\nBuild completed in {:.2f} seconds.\n".format(duration))


if __name__ == "__main__":
    main()
