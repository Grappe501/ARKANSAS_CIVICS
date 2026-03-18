from pathlib import Path
import sys
from datetime import datetime


# ------------------------------------------------
# Ensure project root is importable
# ------------------------------------------------

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


# ------------------------------------------------
# Course engine import
# ------------------------------------------------

from engine.course_engine import CourseEngine  # noqa: E402


def section(title: str) -> None:
    print("\n================================================")
    print(f" {title}")
    print("================================================\n")


def info(message: str) -> None:
    print(f"ℹ {message}")


def success(message: str) -> None:
    print(f"✔ {message}")


def fail(message: str) -> None:
    print(f"\n❌ {message}\n")
    sys.exit(1)


def main() -> None:
    start = datetime.now()

    section("Building Arkansas Civics Course Engine")

    engine = CourseEngine(ROOT)

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
        fail("Course engine build aborted because source structure is invalid")

    success("Platform structure validated")

    section("Generating Internal Course Packages")

    output_paths = engine.export_course_packages()

    output_dir = engine.kernel.exports_dir / "course_engine"
    package_count = len(engine.build_all_course_packages())

    success(f"Course engine packages generated for {package_count} courses")
    info(f"Output directory: {output_dir}")

    print("\nGenerated files:")
    for path in output_paths:
        print(path)

    duration = (datetime.now() - start).total_seconds()

    print("\n------------------------------------")
    print(" COURSE ENGINE BUILD COMPLETE ")
    print("------------------------------------\n")
    print("Generated outputs should appear in:\n")
    print("exports/course_engine/")
    print("\nBuild completed in {:.2f} seconds.\n".format(duration))


if __name__ == "__main__":
    main()