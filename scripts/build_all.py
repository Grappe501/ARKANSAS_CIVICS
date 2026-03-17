import argparse
import os
import subprocess
import sys
from datetime import datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPTS_DIR = os.path.join(ROOT, "scripts")


def section(title: str) -> None:
    print("\n================================================")
    print(f" {title}")
    print("================================================\n")


def run_script(script_name: str) -> None:
    script_path = os.path.join(SCRIPTS_DIR, script_name)
    if not os.path.exists(script_path):
        print(f"⚠ Script not found: {script_name}")
        return

    start = datetime.now()
    print(f"\n▶ Running {script_name}\n")

    try:
        subprocess.run([sys.executable, script_path], check=True)
        duration = (datetime.now() - start).total_seconds()
        print(f"✔ {script_name} complete ({duration:.2f}s)")
    except subprocess.CalledProcessError:
        print(f"\n❌ Error while running {script_name}")
        sys.exit(1)


def check_civic_library() -> None:
    library_dir = os.path.join(ROOT, "data", "civic_library")
    if not os.path.exists(library_dir):
        print("⚠ Civic library directory not found.")
        return
    files = os.listdir(library_dir)
    print(f"✔ Civic knowledge library detected ({len(files)} files)")


def run_sql_seed() -> None:
    sql_path = os.path.join(ROOT, "scripts", "seed_postgres_schema.sql")
    if os.path.exists(sql_path):
        print("\nℹ Postgres schema file detected.")
        print("Run manually with your database client if needed.")
    else:
        print("⚠ No Postgres schema file found.")


def check_dashboard() -> None:
    dashboard_dir = os.path.join(ROOT, "apps", "editor-dashboard")
    if os.path.exists(dashboard_dir):
        print("✔ Editor dashboard detected")
    else:
        print("⚠ Editor dashboard not found")


def show_outputs() -> None:
    print("\n------------------------------------")
    print(" BUILD COMPLETE ")
    print("------------------------------------\n")
    print("Generated outputs should appear in:\n")
    print("exports/book/")
    print("exports/course/")
    print("exports/workbook/")
    print("exports/workshop/")
    print("exports/facilitator/")
    print("exports/reader_site/")
    print("\nDashboard location:")
    print("apps/editor-dashboard/")
    print("\nNetlify deploy folders:")
    print("exports/reader_site/")
    print("apps/editor-dashboard/")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Arkansas Civics Platform Builder")
    parser.add_argument(
        "--with-scaffold",
        action="store_true",
        help="Refresh dashboard templates before running the build pipeline.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    start = datetime.now()

    section("Arkansas Civics Platform Builder")
    print("Project root:")
    print(ROOT)
    print()

    if args.with_scaffold:
        section("OPTIONAL — Refreshing Dashboard Scaffold")
        run_script("scaffold_everything.py")
    else:
        print("Skipping scaffold refresh (safe mode). Use --with-scaffold to rebuild dashboard templates.\n")

    section("STEP 1 — Building Book Manuscript")
    run_script("build_book.py")

    section("STEP 2 — Building Course Export Packages")
    run_script("build_course_exports.py")

    section("STEP 3 — Generating Reader Website")
    run_script("generate_reader_site.py")

    section("STEP 4 — Syncing Editor Dashboard Content")
    run_script("copy_dashboard_content.py")

    section("STEP 5 — Validating Civic Knowledge Library")
    check_civic_library()

    section("STEP 6 — Database Schema")
    run_sql_seed()

    section("STEP 7 — Dashboard Environment")
    check_dashboard()

    duration = (datetime.now() - start).total_seconds()
    show_outputs()
    print(f"Build completed in {duration:.2f} seconds.\n")


if __name__ == "__main__":
    main()
