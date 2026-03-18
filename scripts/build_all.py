import argparse
import subprocess
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from engine.platform_kernel import create_kernel

KERNEL = create_kernel(ROOT)
SCRIPTS_DIR = KERNEL.scripts_dir


def section(title: str) -> None:
    print("\n================================================")
    print(f" {title}")
    print("================================================\n")


def info(msg: str) -> None:
    print(f"[INFO] {msg}")


def warn(msg: str) -> None:
    print(f"[WARN] {msg}")


def success(msg: str) -> None:
    print(f"[OK] {msg}")


def fail(msg: str) -> None:
    print(f"\n[ERROR] {msg}\n")
    sys.exit(1)


def run_script(script_name: str) -> None:
    script_path = SCRIPTS_DIR / script_name
    if not script_path.exists():
        warn(f"Script not found: {script_name}")
        return
    start = datetime.now()
    print(f"\n> Running {script_name}\n")
    try:
        subprocess.run([sys.executable, str(script_path)], check=True)
        duration = (datetime.now() - start).total_seconds()
        success(f"{script_name} complete ({duration:.2f}s)")
    except subprocess.CalledProcessError:
        fail(f"Error while running {script_name}")


def validate_platform_structure() -> None:
    validation = KERNEL.validate_structure()
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
        fail("Platform structure validation failed")
    success("Platform structure validated")


def refresh_dashboard_manifest() -> None:
    manifest_path = KERNEL.write_dashboard_manifest()
    success("Dashboard manifest refreshed via kernel")
    print(manifest_path)


def export_kernel_artifacts() -> None:
    snapshot_path = KERNEL.export_system_snapshot()
    runtime_manifest_path = KERNEL.export_runtime_manifest()
    health_report_path = KERNEL.export_health_report()
    success("Kernel system snapshot written")
    print(snapshot_path)
    success("Kernel runtime manifest written")
    print(runtime_manifest_path)
    success("Kernel health report written")
    print(health_report_path)


def check_civic_library() -> None:
    library_dir = ROOT / "data" / "civic_library"
    if not library_dir.exists():
        warn("Civic library directory not found.")
        return
    files = [p for p in library_dir.iterdir() if p.is_file()]
    success(f"Civic knowledge library detected ({len(files)} files)")


def check_database_schema() -> None:
    sql_path = SCRIPTS_DIR / "seed_postgres_schema.sql"
    if sql_path.exists():
        info("Postgres schema file detected.")
        info("Run manually with your database client if needed.")
    else:
        warn("No Postgres schema file found.")


def check_dashboard_environment() -> None:
    if not KERNEL.dashboard_dir.exists():
        warn("Editor dashboard not found")
        return
    success("Editor dashboard detected")
    if KERNEL.dashboard_manifest_path.exists():
        success("Dashboard manifest detected")
    else:
        warn("Dashboard manifest missing")


def show_outputs(duration: float) -> None:
    print("\n------------------------------------")
    print(" BUILD COMPLETE ")
    print("------------------------------------\n")
    print("Generated outputs should appear in:\n")
    print("exports/book/")
    print("exports/course/")
    print("exports/course_engine/")
    print("exports/lesson_player/")
    print("exports/civic_intelligence_map/")
    print("exports/knowledge_graph/")
    print("exports/reader_site/")
    print("exports/system_map/")
    print("\nDashboard location:")
    print("apps/editor-dashboard/")
    print("\nNetlify deploy folders:")
    print("exports/reader_site/")
    print("apps/editor-dashboard/")
    print(f"\nBuild completed in {duration:.2f} seconds.\n")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Arkansas Civics Platform Builder")
    parser.add_argument("--with-scaffold", action="store_true", help="Refresh dashboard templates before running the build pipeline.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    start = datetime.now()

    section("Arkansas Civics Platform Builder")
    print("Project root:")
    print(ROOT)
    print()

    section("STEP 0 - Platform Kernel Validation")
    try:
        KERNEL.assert_core_paths()
        success("Core platform paths detected")
    except FileNotFoundError as exc:
        fail(f"Kernel path validation failed:\n{exc}")
    validate_platform_structure()

    section("STEP 0B - Platform Health")
    health = KERNEL.get_health_report()
    info(f"Environment: {health.get('environment')}")
    info(f"Health status: {health.get('status')}")

    if args.with_scaffold:
        section("OPTIONAL - Refreshing Dashboard Scaffold")
        run_script("editor_dashboard_generator.py")
    else:
        print("Skipping scaffold refresh (safe mode). Use --with-scaffold to rebuild dashboard templates.\n")

    section("STEP 1 - Building Book Manuscript")
    run_script("build_book.py")

    section("STEP 2 - Building Course Export Packages")
    run_script("build_course_exports.py")

    section("STEP 3 - Building Internal Course Engine")
    run_script("build_course_engine.py")

    section("STEP 4 - Building Lesson Player")
    run_script("build_lesson_player.py")

    section("STEP 5 - Building Civic Intelligence Map")
    run_script("build_civic_intelligence_map.py")

    section("STEP 6 - Building Knowledge Graph")
    run_script("build_knowledge_graph.py")

    section("STEP 7 - Generating Reader Website")
    run_script("generate_reader_site.py")

    section("STEP 8 - Syncing Editor Dashboard Content")
    run_script("copy_dashboard_content.py")

    section("STEP 9 - Refreshing Kernel Dashboard Manifest")
    refresh_dashboard_manifest()

    section("STEP 10 - Exporting Platform Kernel Artifacts")
    export_kernel_artifacts()

    section("STEP 11 - Validating Civic Knowledge Library")
    check_civic_library()

    section("STEP 12 - Database Schema")
    check_database_schema()

    section("STEP 13 - Dashboard Environment")
    check_dashboard_environment()

    duration = (datetime.now() - start).total_seconds()
    show_outputs(duration)


if __name__ == "__main__":
    main()
