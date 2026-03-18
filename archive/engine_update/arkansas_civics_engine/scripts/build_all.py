from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from engine.builders import (
    build_book,
    build_course_manifest,
    build_facilitator_guide,
    build_website_manifest,
    build_workbook,
    build_workshop,
)


def main() -> None:
    outputs = [
        build_book(),
        build_course_manifest(),
        build_workbook(),
        build_workshop(),
        build_facilitator_guide(),
        build_website_manifest(),
    ]
    print('Built outputs:')
    for path in outputs:
        print(f' - {path}')


if __name__ == '__main__':
    main()
