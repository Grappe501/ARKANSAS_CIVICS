from __future__ import annotations

from pathlib import Path
import sys
import json

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from engine.platform_kernel import create_kernel


def main() -> None:
    kernel = create_kernel(ROOT)
    report = kernel.get_health_report()
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
