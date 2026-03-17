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

    const filePath = path.join(
      root,
      "content",
      "courses",
      body.course,
      body.chapter,
      body.segment
    );

    fs.writeFileSync(filePath, body.content || "", "utf-8");

    execSync("python scripts/build_all.py", { cwd: root, stdio: "inherit" });

    const commitName = process.env.GIT_COMMIT_NAME || "Arkansas Civics Bot";
    const commitEmail = process.env.GIT_COMMIT_EMAIL || "bot@example.com";

    execSync(`git config user.name "${commitName}"`, { cwd: root });
    execSync(`git config user.email "${commitEmail}"`, { cwd: root });
    execSync("git add .", { cwd: root });

    try {
      execSync(`git commit -m "Universal content update: ${body.course} ${body.chapter} ${body.segment}"`, { cwd: root });
    } catch (commitErr) {
      // no-op if no changes
    }

    return {
      statusCode: 200,
      body: JSON.stringify({
        message: "Saved, rebuilt, and commit attempted successfully.",
        filePath
      })
    };
  } catch (err) {
    return {
      statusCode: 500,
      body: JSON.stringify({ error: err.message })
    };
  }
};
