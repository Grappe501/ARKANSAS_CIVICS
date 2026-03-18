from pathlib import Path
import shutil
import sys


# ------------------------------------------------
# Ensure project root is importable
# ------------------------------------------------

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


# ------------------------------------------------
# Kernel import
# ------------------------------------------------

from engine.platform_kernel import create_kernel


KERNEL = create_kernel(ROOT)


# ------------------------------------------------
# Utility output helpers
# ------------------------------------------------

def info(msg: str) -> None:
    print(f"ℹ {msg}")


def success(msg: str) -> None:
    print(f"✔ {msg}")


def warn(msg: str) -> None:
    print(f"⚠ {msg}")


def fail(msg: str) -> None:
    print(f"\n❌ {msg}\n")
    sys.exit(1)


# ------------------------------------------------
# Copy dashboard mirror
# ------------------------------------------------

def rebuild_dashboard_content() -> None:

    source_courses = KERNEL.courses_dir
    dashboard_dir = KERNEL.dashboard_content_dir

    if not source_courses.exists():
        fail("Content courses directory not found.")

    # Remove existing dashboard mirror
    if dashboard_dir.exists():
        info("Removing previous dashboard mirror...")
        shutil.rmtree(dashboard_dir)

    dashboard_dir.mkdir(parents=True, exist_ok=True)

    courses = KERNEL.load_all_courses()

    copied_segments = 0

    for course in courses:

        course_out = dashboard_dir / course.slug
        course_out.mkdir(parents=True, exist_ok=True)

        for chapter in course.chapters:

            chapter_out = course_out / chapter.slug
            chapter_out.mkdir(parents=True, exist_ok=True)

            seg_out = chapter_out / "segments"
            seg_out.mkdir(parents=True, exist_ok=True)

            for segment in chapter.segments:

                src = segment.path
                dst = seg_out / src.name

                shutil.copy2(src, dst)
                copied_segments += 1

    success("Dashboard content mirror rebuilt")
    print(f"Segments copied: {copied_segments}")
    print(f"Mirror location: {dashboard_dir}")


# ------------------------------------------------
# Manifest generation
# ------------------------------------------------

def regenerate_dashboard_manifest() -> None:

    manifest_path = KERNEL.write_dashboard_manifest()

    success("Dashboard manifest regenerated from kernel")
    print(manifest_path)


# ------------------------------------------------
# Main
# ------------------------------------------------

def main():

    print("\n====================================")
    print(" Dashboard Content Sync")
    print("====================================\n")

    # Validate kernel paths
    try:
        KERNEL.assert_core_paths()
    except FileNotFoundError as exc:
        fail(str(exc))

    # Validate content structure
    validation = KERNEL.validate_structure()

    if not validation.get("ok", False):

        warn("Platform structure issues detected:\n")

        for issue in validation.get("issues", []):
            print(f"- {issue}")

        print()

    rebuild_dashboard_content()

    regenerate_dashboard_manifest()

    print("\nDashboard sync complete.\n")


# ------------------------------------------------

if __name__ == "__main__":
    main()