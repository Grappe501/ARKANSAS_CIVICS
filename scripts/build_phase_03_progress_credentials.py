from pathlib import Path
import sys
from datetime import datetime
import traceback

# ------------------------------------------------
# Path Setup
# ------------------------------------------------

ROOT = Path(__file__).resolve().parents[1]

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

# ------------------------------------------------
# Engine Imports
# ------------------------------------------------

from engine.platform_kernel import create_kernel  # noqa: E402
from engine.progress_registry import ProgressRegistry  # noqa: E402
from engine.civic_credential_engine import CivicCredentialEngine  # noqa: E402


# ------------------------------------------------
# Console Helpers
# ------------------------------------------------

def section(title: str) -> None:
    print("\n================================================")
    print(f" {title}")
    print("================================================\n")


def ok(message: str) -> None:
    print(f"[OK] {message}")


def info(message: str) -> None:
    print(f"[INFO] {message}")


def warn(message: str) -> None:
    print(f"[WARN] {message}")


def fail(message: str) -> None:
    print(f"[ERROR] {message}")


# ------------------------------------------------
# Phase 03 Builder
# ------------------------------------------------

def main() -> None:
    start = datetime.now()

    try:

        section("Phase 03 - Progress Registry and Credentials")

        # ------------------------------------------------
        # Initialize Kernel
        # ------------------------------------------------

        kernel = create_kernel(ROOT)
        registry = ProgressRegistry(ROOT)
        credentials = CivicCredentialEngine(ROOT)

        kernel.assert_core_paths()
        ok("Core platform paths detected")

        # ------------------------------------------------
        # Validate Platform Structure
        # ------------------------------------------------

        validation = kernel.validate_structure()
        summary = validation.get("summary", {})

        print("Structure summary:")
        print(f"  Courses:  {summary.get('course_count', 0)}")
        print(f"  Chapters: {summary.get('chapter_count', 0)}")
        print(f"  Segments: {summary.get('segment_count', 0)}")

        if not validation.get("ok", False):
            warn("Platform validation returned issues")
            for issue in validation.get("issues", []):
                print(f" - {issue}")
        else:
            ok("Platform structure validated")

        # ------------------------------------------------
        # Export Progress Registry
        # ------------------------------------------------

        section("Exporting Progress Registry")

        registry_outputs = registry.export_registry_index()

        ok("Progress registry exported")

        # ------------------------------------------------
        # Export Credential System
        # ------------------------------------------------

        section("Exporting Civic Credentials")

        credential_outputs = credentials.export_index()

        ok("Credential index exported")

        # ------------------------------------------------
        # Output Files
        # ------------------------------------------------

        print("\nGenerated files:")

        for path in [*registry_outputs, *credential_outputs]:
            print(path)

        # ------------------------------------------------
        # Build Complete
        # ------------------------------------------------

        duration = (datetime.now() - start).total_seconds()

        print("\n--------------------------------------------")
        print(" PHASE 03 PROGRESS + CREDENTIALS COMPLETE")
        print("--------------------------------------------\n")

        info(f"Environment: {kernel.environment}")
        info(f"Progress registry directory: {registry.progress_profiles_dir}")
        info(f"Credential exports directory: {credentials.export_dir}")
        info(f"Build completed in {duration:.2f} seconds")

    except Exception as e:

        fail("Phase 03 build failed")

        print("\nException details:\n")
        traceback.print_exc()

        raise SystemExit(1)


# ------------------------------------------------
# Entry Point
# ------------------------------------------------

if __name__ == "__main__":
    main()