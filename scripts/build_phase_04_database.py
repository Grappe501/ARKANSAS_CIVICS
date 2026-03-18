from pathlib import Path
import sys
from datetime import datetime
import traceback

ROOT = Path(__file__).resolve().parents[1]

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from engine.migration_engine import MigrationEngine


def section(title):
    print("\n================================================")
    print(f" {title}")
    print("================================================\n")


def ok(msg):
    print(f"[OK] {msg}")


def info(msg):
    print(f"[INFO] {msg}")


def fail(msg):
    print(f"[ERROR] {msg}")


def main():

    start = datetime.now()

    try:

        section("Phase 04 — Database Infrastructure")

        engine = MigrationEngine(ROOT)

        print("Running database migrations...\n")

        engine.run()

        ok("Database migrations completed")

        duration = (datetime.now() - start).total_seconds()

        print("\n--------------------------------------------")
        print(" PHASE 04 DATABASE BUILD COMPLETE")
        print("--------------------------------------------\n")

        info(f"Migration directory: {ROOT / 'database' / 'migrations'}")
        info(f"Build completed in {duration:.2f} seconds")

    except Exception:

        fail("Database build failed\n")

        traceback.print_exc()

        raise SystemExit(1)


if __name__ == "__main__":
    main()