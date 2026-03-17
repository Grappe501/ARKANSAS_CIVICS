import json
import subprocess
import os
from pathlib import Path

ROOT = Path(os.environ.get("ARKANSAS_CIVICS_ROOT", "."))

GENERATOR = ROOT / "scripts" / "generate_autonomous_civic_course.py"

def handler(event, context):

    try:

        body = json.loads(event.get("body") or "{}")

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
            return {
                "statusCode": 500,
                "body": json.dumps({
                    "error": result.stderr
                })
            }

        return {
            "statusCode": 200,
            "body": json.dumps({
                "message": "Course generation complete",
                "stdout": result.stdout
            })
        }

    except Exception as e:

        return {
            "statusCode": 500,
            "body": json.dumps({
                "error": str(e)
            })
        }