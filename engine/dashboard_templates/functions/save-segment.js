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

    const filePath = path.join(
      root,
      "content",
      "courses",
      body.course,
      body.chapter,
      body.segment
    );

    fs.writeFileSync(filePath, body.content || "", "utf-8");

    return {
      statusCode: 200,
      body: JSON.stringify({ message: `Saved ${filePath}` })
    };
  } catch (err) {
    return {
      statusCode: 500,
      body: JSON.stringify({ error: err.message })
    };
  }
};
