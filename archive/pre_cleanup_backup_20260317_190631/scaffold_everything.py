from pathlib import Path
import shutil
import json

ROOT = Path(__file__).resolve().parents[1]

TEMPLATE_DIR = ROOT / "engine" / "dashboard_templates"
FUNCTION_TEMPLATE_DIR = TEMPLATE_DIR / "functions"

APP_DIR = ROOT / "apps" / "editor-dashboard"
FUNCTIONS_DIR = ROOT / "netlify" / "functions"

CONTENT_MANIFEST = APP_DIR / "content-manifest.json"

AUTONOMOUS_GENERATOR = ROOT / "scripts" / "generate_autonomous_civic_course.py"


# --------------------------------------------------
# Utility
# --------------------------------------------------

def copy_tree(src: Path, dst: Path):
    if not src.exists():
        raise FileNotFoundError(f"Template source not found: {src}")
    shutil.copytree(src, dst, dirs_exist_ok=True)


def ensure_content_manifest():
    if not CONTENT_MANIFEST.exists():
        CONTENT_MANIFEST.write_text("{}", encoding="utf-8")


# --------------------------------------------------
# Dashboard API Function
# --------------------------------------------------

def create_autonomous_generator_function():

    fn_path = FUNCTIONS_DIR / "generate-course.py"

    code = f"""
import json
import subprocess
import os
from pathlib import Path

ROOT = Path(os.environ.get("ARKANSAS_CIVICS_ROOT", "."))

GENERATOR = ROOT / "scripts" / "generate_autonomous_civic_course.py"

def handler(event, context):

    try:

        body = json.loads(event.get("body") or "{{}}")

        brief_file = body.get("brief")

        cmd = ["python", str(GENERATOR)]

        if brief_file:
            cmd.append(brief_file)

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            cwd=str(ROOT)
        )

        if result.returncode != 0:
            return {{
                "statusCode": 500,
                "body": json.dumps({{
                    "error": result.stderr
                }})
            }}

        return {{
            "statusCode": 200,
            "body": json.dumps({{
                "message": "Course generation complete",
                "stdout": result.stdout
            }})
        }}

    except Exception as e:

        return {{
            "statusCode": 500,
            "body": json.dumps({{
                "error": str(e)
            }})
        }}
"""

    fn_path.write_text(code.strip(), encoding="utf-8")


# --------------------------------------------------
# Dashboard Button UI
# --------------------------------------------------

def create_dashboard_ui_hook():

    ui_file = APP_DIR / "generate-course.js"

    code = """
export async function generateCourse(brief=null){

    const response = await fetch("/.netlify/functions/generate-course",{
        method:"POST",
        headers:{ "Content-Type":"application/json" },
        body:JSON.stringify({ brief })
    })

    const data = await response.json()

    if(!response.ok){
        console.error(data)
        alert("Course generation failed.")
        return
    }

    console.log(data)
    alert("Course generation complete.")
}
"""

    ui_file.write_text(code.strip(), encoding="utf-8")


# --------------------------------------------------
# Dashboard Panel
# --------------------------------------------------

def create_dashboard_panel():

    panel = APP_DIR / "autonomous-course-panel.html"

    html = """
<div class="panel">

<h2>Autonomous Course Generator</h2>

<p>Create a complete civic course automatically.</p>

<button id="generate-course">
Generate New Course
</button>

<script type="module">

import { generateCourse } from "./generate-course.js"

document.getElementById("generate-course")
.addEventListener("click", () => {

    const brief = prompt(
        "Optional course brief YAML path (leave blank for default)"
    )

    generateCourse(brief || null)

})

</script>

</div>
"""

    panel.write_text(html.strip(), encoding="utf-8")


# --------------------------------------------------
# Dashboard Menu Link
# --------------------------------------------------

def attach_dashboard_menu():

    menu_file = APP_DIR / "index.html"

    if not menu_file.exists():
        return

    text = menu_file.read_text(encoding="utf-8")

    if "autonomous-course-panel.html" in text:
        return

    injection = """
<a href="autonomous-course-panel.html">
Autonomous Course Generator
</a>
"""

    text = text.replace(
        "</nav>",
        injection + "\n</nav>"
    )

    menu_file.write_text(text, encoding="utf-8")


# --------------------------------------------------
# Main
# --------------------------------------------------

def main():

    APP_DIR.mkdir(parents=True, exist_ok=True)
    FUNCTIONS_DIR.mkdir(parents=True, exist_ok=True)

    copy_tree(TEMPLATE_DIR, APP_DIR)
    copy_tree(FUNCTION_TEMPLATE_DIR, FUNCTIONS_DIR)

    ensure_content_manifest()

    create_autonomous_generator_function()

    create_dashboard_ui_hook()

    create_dashboard_panel()

    attach_dashboard_menu()

    print("\nEditor dashboard scaffold generated.\n")

    print(f"Frontend: {APP_DIR}")
    print(f"Functions: {FUNCTIONS_DIR}")

    print("\nNew capability added:")
    print("✔ Autonomous course generator integrated into dashboard")

    print("\nNext steps:")

    print("1. Run: python scripts/copy_dashboard_content.py")

    print("2. Set Netlify environment variables:")
    print("   - OPENAI_API_KEY")
    print("   - ARKANSAS_CIVICS_ROOT")
    print("   - GIT_COMMIT_NAME")
    print("   - GIT_COMMIT_EMAIL")

    print("3. Deploy repo to Netlify")

    print("4. Publish folder: apps/editor-dashboard")

    print("5. Functions folder: netlify/functions")

    print("\nDashboard will now include:")
    print("• Generate New Course")
    print("• Automatic AI curriculum generation")
    print("• Course factory pipeline integration")


if __name__ == "__main__":
    main()