const { execSync } = require("child_process");
const fs = require("fs");
const path = require("path");

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

    execSync(
      `python scripts/generate_chapter_context.py ${body.course} ${body.chapter}`,
      { cwd: root, stdio: "inherit" }
    );

    const contextFile = path.join(
      root,
      "docs",
      "chapter_context",
      `${body.course}_${body.chapter}_context.md`
    );

    let output = "No context file found.";
    if (fs.existsSync(contextFile)) {
      output = fs.readFileSync(contextFile, "utf-8");
    }

    return {
      statusCode: 200,
      body: JSON.stringify({ output })
    };
  } catch (err) {
    return {
      statusCode: 500,
      body: JSON.stringify({ error: err.message })
    };
  }
};
