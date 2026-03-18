from __future__ import annotations

from pathlib import Path
from datetime import datetime
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from engine.platform_kernel import create_kernel


KERNEL = create_kernel(ROOT)


def section(title: str) -> None:
    print("\n================================================")
    print(f" {title}")
    print("================================================\n")


def success(message: str) -> None:
    print(f"[OK] {message}")


def info(message: str) -> None:
    print(f"[INFO] {message}")


def fail(message: str) -> None:
    print(f"\n[ERROR] {message}\n")
    sys.exit(1)


def main() -> None:
    start = datetime.now()
    section("Phase 01 - Core Kernel Stabilization")

    try:
        KERNEL.assert_core_paths()
        success("Core platform paths detected")
    except FileNotFoundError as exc:
        fail(str(exc))

    validation = KERNEL.validate_structure()
    summary = validation.get("summary", {})
    print("Structure summary:")
    print(f"  Courses:  {summary.get('course_count', 0)}")
    print(f"  Chapters: {summary.get('chapter_count', 0)}")
    print(f"  Segments: {summary.get('segment_count', 0)}")
    if not validation.get("ok", False):
        for issue in validation.get("issues", []):
            print(f"- {issue}")
        fail("Platform structure validation failed")
    success("Platform structure validated")

    section("Exporting Kernel Runtime Artifacts")
    manifest_path = KERNEL.write_dashboard_manifest()
    snapshot_path = KERNEL.export_system_snapshot()
    runtime_manifest_path = KERNEL.export_runtime_manifest()
    health_report_path = KERNEL.export_health_report()

    success("Dashboard manifest exported")
    success("System snapshot exported")
    success("Runtime manifest exported")
    success("Health report exported")

    print("\nGenerated files:")
    for path in [manifest_path, snapshot_path, runtime_manifest_path, health_report_path]:
        print(path)

    duration = (datetime.now() - start).total_seconds()
    print("\n--------------------------------------------")
    print(" PHASE 01 KERNEL STABILIZATION COMPLETE")
    print("--------------------------------------------\n")
    info(f"Environment: {KERNEL.environment_name}")
    info(f"Logs directory: {KERNEL.logs_dir}")
    info(f"Build completed in {duration:.2f} seconds")


if __name__ == "__main__":
    main()
