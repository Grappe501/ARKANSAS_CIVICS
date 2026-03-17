        exports.handler = async (event) => {
          try {
            const body = JSON.parse(event.body || "{}");
            const apiKey = process.env.OPENAI_API_KEY;

            if (!apiKey) {
              return {
                statusCode: 500,
                body: JSON.stringify({ error: "Missing OPENAI_API_KEY" })
              };
            }

            const prompt = `
You are assisting with an Arkansas civics writing platform.

Mode: ${body.mode || "suggest"}
Course: ${body.course || ""}
Chapter: ${body.chapter || ""}
Segment: ${body.segment || ""}

Instruction:
${body.instruction || ""}

Current text:
${body.currentText || ""}
`;

            const response = await fetch("https://api.openai.com/v1/responses", {
              method: "POST",
              headers: {
                "Content-Type": "application/json",
                "Authorization": `Bearer ${apiKey}`
              },
              body: JSON.stringify({
                model: "gpt-5",
                input: prompt
              })
            });

            const data = await response.json();

            let output = "No output returned.";
            if (data.output_text) {
              output = data.output_text;
            } else if (data.output && Array.isArray(data.output)) {
              output = JSON.stringify(data.output, null, 2);
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
