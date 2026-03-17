from __future__ import annotations
from pathlib import Path
import hashlib
import json

ROOT = Path(__file__).resolve().parents[1]
DASH = ROOT / "apps" / "editor-dashboard"
MANIFEST = DASH / "content-manifest.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def validate_manifest() -> list[str]:
    issues: list[str] = []
    if not MANIFEST.exists():
        return [f"Missing manifest: {MANIFEST}"]
    data = json.loads(MANIFEST.read_text(encoding="utf-8"))
    for course, chapters in data.items():
        for chapter, segments in chapters.items():
            for seg in segments:
                p = DASH / "content" / course / chapter / seg
                if not p.exists():
                    issues.append(str(p.relative_to(ROOT)))
    return issues


def compare_duplicate_scripts() -> list[str]:
    pairs = [
        ("scripts/generate_autonomous_civic_course.py", "scripts/generate_course_factory_suite.py"),
        ("netlify/functions/save-segment.js", "apps/editor-dashboard/functions/save-segment.js"),
        ("netlify/functions/commit-universal.js", "apps/editor-dashboard/functions/commit-universal.js"),
    ]
    out = []
    for a, b in pairs:
        pa = ROOT / a
        pb = ROOT / b
        if pa.exists() and pb.exists() and sha256(pa) == sha256(pb):
            out.append(f"DUPLICATE {a} == {b}")
    return out


def main() -> None:
    print("ARKANSAS CIVICS REPO VALIDATION\n")
    print(f"Root: {ROOT}")
    print(f"config/course_factory exists: {(ROOT / 'config' / 'course_factory').exists()}")
    print()

    issues = validate_manifest()
    print(f"Dashboard manifest missing paths: {len(issues)}")
    for issue in issues[:20]:
        print(f" - {issue}")
    if len(issues) > 20:
        print(f" ... {len(issues)-20} more")
    print()

    dups = compare_duplicate_scripts()
    print("Known duplicate files:")
    for item in dups:
        print(f" - {item}")
    if not dups:
        print(" - none")


if __name__ == "__main__":
    main()
