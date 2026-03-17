const fs = require("fs");
const path = require("path");
const { execSync } = require("child_process");

exports.handler = async (event) => {
  try {
    const body = JSON.parse(event.body || "{}");
    const root = process.env.ARKANSAS_CIVICS_ROOT;

    if (!root) {
      return {
        statusCode: 500,
        body: JSON.stringify({ error: "Missing ARKANSAS_CIVICS_ROOT" })
      };
    }

    const tmpDir = path.join(root, "exports", "rise_requests");
    fs.mkdirSync(tmpDir, { recursive: true });

    const requestPath = path.join(
      tmpDir,
      `${body.course}_${body.chapter}_${Date.now()}.json`
    );

    fs.writeFileSync(requestPath, JSON.stringify(body, null, 2), "utf-8");

    execSync(`python scripts/export_rise_course.py "${requestPath}"`, {
      cwd: root,
      stdio: "inherit"
    });

    return {
      statusCode: 200,
      body: JSON.stringify({
        message: "Rise export requested successfully.",
        requestPath
      })
    };
  } catch (err) {
    return {
      statusCode: 500,
      body: JSON.stringify({ error: err.message })
    };
  }
};
