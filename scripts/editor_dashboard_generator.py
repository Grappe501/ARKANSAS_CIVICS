from pathlib import Path
import shutil

ROOT = Path(__file__).resolve().parents[1]
TEMPLATE_DIR = ROOT / "engine" / "dashboard_templates"
FUNCTION_TEMPLATE_DIR = TEMPLATE_DIR / "functions"

APP_DIR = ROOT / "apps" / "editor-dashboard"
FUNCTIONS_DIR = ROOT / "netlify" / "functions"

def copy_tree(src: Path, dst: Path):
    if not src.exists():
        raise FileNotFoundError(f"Template source not found: {src}")
    shutil.copytree(src, dst, dirs_exist_ok=True)

def ensure_content_manifest():
    manifest = APP_DIR / "content-manifest.json"
    if not manifest.exists():
        manifest.write_text("{}", encoding="utf-8")

def main():
    APP_DIR.mkdir(parents=True, exist_ok=True)
    FUNCTIONS_DIR.mkdir(parents=True, exist_ok=True)

    copy_tree(TEMPLATE_DIR, APP_DIR)
    copy_tree(FUNCTION_TEMPLATE_DIR, FUNCTIONS_DIR)

    ensure_content_manifest()

    print("\nEditor dashboard scaffold generated.\n")
    print(f"Frontend: {APP_DIR}")
    print(f"Functions: {FUNCTIONS_DIR}")
    print("\nNext steps:")
    print("1. Run: python scripts/copy_dashboard_content.py")
    print("2. Set Netlify environment variables:")
    print("   - OPENAI_API_KEY")
    print("   - ARKANSAS_CIVICS_ROOT")
    print("   - GIT_COMMIT_NAME")
    print("   - GIT_COMMIT_EMAIL")
    print("3. Deploy the repo to Netlify.")
    print("4. Publish folder: apps/editor-dashboard")
    print("5. Functions folder: netlify/functions")
    print("6. Use export-rise.js + export_rise_course.py for Articulate-ready lesson output")

if __name__ == "__main__":
    main()
