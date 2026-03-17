from pathlib import Path
from textwrap import dedent
from datetime import datetime
import shutil

ROOT = Path(__file__).resolve().parents[1]

SCRIPTS_DIR = ROOT / "scripts"
ENGINE_DIR = ROOT / "engine"
TEMPLATE_DIR = ENGINE_DIR / "dashboard_templates"
FUNCTION_TEMPLATE_DIR = TEMPLATE_DIR / "functions"

APP_DIR = ROOT / "apps" / "editor-dashboard"
FUNCTIONS_DIR = ROOT / "netlify" / "functions"

GENERATOR_PATH = SCRIPTS_DIR / "editor_dashboard_generator.py"
BACKUP_DIR = ROOT / "backups" / "dashboard_generator"
BACKUP_DIR.mkdir(parents=True, exist_ok=True)


FILES = {
    TEMPLATE_DIR / "index.html": dedent("""\
        <!DOCTYPE html>
        <html lang="en">
        <head>
          <meta charset="UTF-8" />
          <meta name="viewport" content="width=device-width, initial-scale=1.0" />
          <title>Arkansas Civics Editor Dashboard</title>
          <link rel="stylesheet" href="./styles.css" />
        </head>
        <body>
          <div id="app">
            <aside class="sidebar">
              <div class="sidebar-header">
                <h1>Arkansas Civics</h1>
                <p>Editor Dashboard</p>
              </div>

              <div class="sidebar-section">
                <label for="courseSelect">Course</label>
                <select id="courseSelect"></select>
              </div>

              <div class="sidebar-section">
                <label for="chapterSelect">Chapter</label>
                <select id="chapterSelect"></select>
              </div>

              <div class="sidebar-section">
                <label for="segmentSelect">Segment</label>
                <select id="segmentSelect"></select>
              </div>

              <div class="sidebar-section">
                <button id="loadSegmentBtn">Load Segment</button>
                <button id="loadContextBtn" class="secondary">Load Chapter Context</button>
              </div>

              <div class="sidebar-section">
                <h3>Research Tools</h3>
                <button id="researchBtn" class="secondary">Research</button>
                <button id="suggestBtn" class="secondary">Suggest Rewrite</button>
                <button id="storyBtn" class="secondary">Insert Story Ideas</button>
              </div>

              <div class="sidebar-section">
                <h3>Course Factory</h3>
                <button id="generateLessonBtn" class="secondary">Generate Lesson</button>
                <button id="generateQuizBtn" class="secondary">Generate Quiz</button>
                <button id="exportRiseBtn" class="secondary">Export Rise Lesson</button>
              </div>
            </aside>

            <main class="workspace">
              <header class="toolbar">
                <div class="toolbar-left">
                  <span id="activePath">No segment loaded</span>
                </div>
                <div class="toolbar-right">
                  <button id="saveBtn">Save Draft</button>
                  <button id="rebuildBtn" class="secondary">Rebuild</button>
                  <button id="commitBtn" class="primary">Commit Universal</button>
                </div>
              </header>

              <section class="split-layout">
                <div class="panel review-panel">
                  <div class="panel-header">
                    <h2>Current Segment</h2>
                  </div>
                  <div id="currentSegmentView" class="panel-body markdown-view">
                    Select a segment to begin.
                  </div>
                </div>

                <div class="panel right-stack">
                  <div class="panel ai-panel">
                    <div class="panel-header">
                      <h2>AI Suggestions / Research</h2>
                    </div>
                    <div id="aiOutput" class="panel-body">
                      AI output will appear here.
                    </div>
                  </div>

                  <div class="panel editor-panel">
                    <div class="panel-header">
                      <h2>Writing Workspace</h2>
                    </div>
                    <textarea id="editor" class="panel-body editor-textarea" placeholder="Write here..."></textarea>
                  </div>
                </div>
              </section>

              <section class="prompt-bar">
                <div class="prompt-top">
                  <label for="instructionInput">Instruction / Prompt</label>
                </div>
                <div class="prompt-bottom">
                  <textarea id="instructionInput" placeholder="Ask for revisions, additions, deletions, personal stories, research, demographic overlays, movement examples, lesson generation, quizzes, or exports..."></textarea>
                </div>
              </section>
            </main>
          </div>

          <script src="./app.js" type="module"></script>
        </body>
        </html>
    """),

    TEMPLATE_DIR / "styles.css": dedent("""\
        :root {
          --bg: #0f172a;
          --panel: #111827;
          --panel-2: #1f2937;
          --text: #e5e7eb;
          --muted: #94a3b8;
          --accent: #38bdf8;
          --accent-2: #22c55e;
          --border: #334155;
          --danger: #ef4444;
        }

        * { box-sizing: border-box; }

        body {
          margin: 0;
          font-family: Inter, Arial, sans-serif;
          background: var(--bg);
          color: var(--text);
        }

        #app {
          display: grid;
          grid-template-columns: 290px 1fr;
          min-height: 100vh;
        }

        .sidebar {
          background: var(--panel);
          border-right: 1px solid var(--border);
          padding: 20px;
          overflow-y: auto;
        }

        .sidebar-header h1 {
          margin: 0 0 6px 0;
          font-size: 1.4rem;
        }

        .sidebar-header p {
          margin: 0 0 20px 0;
          color: var(--muted);
          font-size: 0.95rem;
        }

        .sidebar-section {
          margin-bottom: 18px;
        }

        .sidebar-section h3 {
          margin: 0 0 10px 0;
          font-size: 0.95rem;
          color: var(--muted);
        }

        label {
          display: block;
          margin-bottom: 6px;
          font-size: 0.9rem;
          color: var(--muted);
        }

        select, textarea, button {
          width: 100%;
          border-radius: 10px;
          border: 1px solid var(--border);
          background: var(--panel-2);
          color: var(--text);
          padding: 10px 12px;
          font-size: 0.95rem;
        }

        button {
          cursor: pointer;
          margin-bottom: 8px;
          transition: 0.15s ease;
        }

        button:hover {
          border-color: var(--accent);
        }

        button.primary {
          background: var(--accent-2);
          color: #06130a;
          font-weight: 600;
        }

        button.secondary {
          background: transparent;
        }

        .workspace {
          display: grid;
          grid-template-rows: auto 1fr auto;
          min-height: 100vh;
        }

        .toolbar {
          display: flex;
          justify-content: space-between;
          align-items: center;
          padding: 14px 18px;
          border-bottom: 1px solid var(--border);
          background: rgba(17,24,39,0.8);
          backdrop-filter: blur(10px);
          position: sticky;
          top: 0;
          z-index: 10;
        }

        .toolbar-right {
          display: flex;
          gap: 10px;
        }

        .toolbar-right button {
          width: auto;
          min-width: 120px;
          margin: 0;
        }

        .split-layout {
          display: grid;
          grid-template-columns: 1fr 1fr;
          gap: 16px;
          padding: 16px;
          min-height: 0;
        }

        .panel {
          background: var(--panel);
          border: 1px solid var(--border);
          border-radius: 16px;
          overflow: hidden;
          min-height: 0;
        }

        .panel-header {
          padding: 12px 16px;
          border-bottom: 1px solid var(--border);
          background: rgba(255,255,255,0.02);
        }

        .panel-header h2 {
          margin: 0;
          font-size: 1rem;
        }

        .panel-body {
          padding: 16px;
          overflow-y: auto;
          min-height: 200px;
          height: 100%;
        }

        .markdown-view {
          white-space: pre-wrap;
          line-height: 1.65;
        }

        .right-stack {
          display: grid;
          grid-template-rows: 1fr 1fr;
          gap: 16px;
          background: transparent;
          border: none;
        }

        .ai-panel, .editor-panel {
          min-height: 0;
        }

        .editor-textarea {
          width: 100%;
          height: 100%;
          min-height: 260px;
          resize: vertical;
          border: none;
          outline: none;
          border-radius: 0;
          background: transparent;
        }

        .prompt-bar {
          padding: 0 16px 16px 16px;
        }

        .prompt-top {
          margin-bottom: 8px;
        }

        .prompt-bottom textarea {
          min-height: 110px;
        }

        @media (max-width: 1200px) {
          #app {
            grid-template-columns: 1fr;
          }

          .sidebar {
            border-right: none;
            border-bottom: 1px solid var(--border);
          }

          .split-layout {
            grid-template-columns: 1fr;
          }
        }
    """),

    TEMPLATE_DIR / "app.js": dedent("""\
        const state = {
          manifest: null,
          currentCourse: null,
          currentChapter: null,
          currentSegment: null,
          currentPath: null
        };

        const courseSelect = document.getElementById("courseSelect");
        const chapterSelect = document.getElementById("chapterSelect");
        const segmentSelect = document.getElementById("segmentSelect");
        const currentSegmentView = document.getElementById("currentSegmentView");
        const aiOutput = document.getElementById("aiOutput");
        const editor = document.getElementById("editor");
        const instructionInput = document.getElementById("instructionInput");
        const activePath = document.getElementById("activePath");

        async function loadManifest() {
          try {
            const res = await fetch("./content-manifest.json");
            if (!res.ok) {
              throw new Error("Manifest not found");
            }
            state.manifest = await res.json();
            populateCourses();
          } catch (err) {
            console.error(err);
            aiOutput.textContent = "Manifest could not be loaded.";
          }
        }

        function populateCourses() {
          courseSelect.innerHTML = "";
          Object.keys(state.manifest || {}).forEach(course => {
            const opt = document.createElement("option");
            opt.value = course;
            opt.textContent = course;
            courseSelect.appendChild(opt);
          });
          state.currentCourse = courseSelect.value;
          populateChapters();
        }

        function populateChapters() {
          chapterSelect.innerHTML = "";
          const chapters = state.manifest?.[state.currentCourse] || {};
          Object.keys(chapters).forEach(chapter => {
            const opt = document.createElement("option");
            opt.value = chapter;
            opt.textContent = chapter;
            chapterSelect.appendChild(opt);
          });
          state.currentChapter = chapterSelect.value;
          populateSegments();
        }

        function populateSegments() {
          segmentSelect.innerHTML = "";
          const segments = state.manifest?.[state.currentCourse]?.[state.currentChapter] || [];
          segments.forEach(segment => {
            const opt = document.createElement("option");
            opt.value = segment;
            opt.textContent = segment;
            segmentSelect.appendChild(opt);
          });
          state.currentSegment = segmentSelect.value;
        }

        async function loadSegment() {
          try {
            const path = `./content/${state.currentCourse}/${state.currentChapter}/${state.currentSegment}`;
            state.currentPath = path;
            activePath.textContent = path;
            const res = await fetch(path);
            if (!res.ok) {
              throw new Error("Segment not found");
            }
            const text = await res.text();
            currentSegmentView.textContent = text;
            editor.value = text;
          } catch (err) {
            aiOutput.textContent = "Segment load failed.";
          }
        }

        async function loadChapterContext() {
          try {
            const payload = {
              course: state.currentCourse,
              chapter: state.currentChapter
            };
            const res = await fetch("/.netlify/functions/chapter-context", {
              method: "POST",
              headers: { "Content-Type": "application/json" },
              body: JSON.stringify(payload)
            });
            const data = await res.json();
            aiOutput.textContent = data.output || "No context returned.";
          } catch (err) {
            aiOutput.textContent = "Context load failed.";
          }
        }

        async function runOpenAIAction(mode) {
          try {
            const payload = {
              mode,
              instruction: instructionInput.value,
              currentText: editor.value,
              course: state.currentCourse,
              chapter: state.currentChapter,
              segment: state.currentSegment
            };
            aiOutput.textContent = "Working...";
            const res = await fetch("/.netlify/functions/openai-proxy", {
              method: "POST",
              headers: { "Content-Type": "application/json" },
              body: JSON.stringify(payload)
            });
            const data = await res.json();
            aiOutput.textContent = data.output || "No response returned.";
          } catch (err) {
            aiOutput.textContent = "AI request failed.";
          }
        }

        async function saveDraft() {
          try {
            const payload = {
              course: state.currentCourse,
              chapter: state.currentChapter,
              segment: state.currentSegment,
              content: editor.value
            };
            const res = await fetch("/.netlify/functions/save-segment", {
              method: "POST",
              headers: { "Content-Type": "application/json" },
              body: JSON.stringify(payload)
            });
            const data = await res.json();
            aiOutput.textContent = data.message || "Saved.";
            currentSegmentView.textContent = editor.value;
          } catch (err) {
            aiOutput.textContent = "Save failed.";
          }
        }

        async function commitUniversal() {
          try {
            const payload = {
              course: state.currentCourse,
              chapter: state.currentChapter,
              segment: state.currentSegment,
              content: editor.value
            };
            aiOutput.textContent = "Saving, rebuilding, and committing...";
            const res = await fetch("/.netlify/functions/commit-universal", {
              method: "POST",
              headers: { "Content-Type": "application/json" },
              body: JSON.stringify(payload)
            });
            const data = await res.json();
            aiOutput.textContent = JSON.stringify(data, null, 2);
            currentSegmentView.textContent = editor.value;
          } catch (err) {
            aiOutput.textContent = "Commit failed.";
          }
        }

        async function exportRiseLesson() {
          try {
            const payload = {
              course: state.currentCourse,
              chapter: state.currentChapter,
              segment: state.currentSegment,
              content: editor.value,
              instruction: instructionInput.value
            };
            aiOutput.textContent = "Exporting Rise lesson...";
            const res = await fetch("/.netlify/functions/export-rise", {
              method: "POST",
              headers: { "Content-Type": "application/json" },
              body: JSON.stringify(payload)
            });
            const data = await res.json();
            aiOutput.textContent = JSON.stringify(data, null, 2);
          } catch (err) {
            aiOutput.textContent = "Rise export failed.";
          }
        }

        courseSelect.addEventListener("change", () => {
          state.currentCourse = courseSelect.value;
          populateChapters();
        });

        chapterSelect.addEventListener("change", () => {
          state.currentChapter = chapterSelect.value;
          populateSegments();
        });

        segmentSelect.addEventListener("change", () => {
          state.currentSegment = segmentSelect.value;
        });

        document.getElementById("loadSegmentBtn").addEventListener("click", loadSegment);
        document.getElementById("loadContextBtn").addEventListener("click", loadChapterContext);
        document.getElementById("researchBtn").addEventListener("click", () => runOpenAIAction("research"));
        document.getElementById("suggestBtn").addEventListener("click", () => runOpenAIAction("suggest"));
        document.getElementById("storyBtn").addEventListener("click", () => runOpenAIAction("story"));
        document.getElementById("generateLessonBtn").addEventListener("click", () => runOpenAIAction("generate_lesson"));
        document.getElementById("generateQuizBtn").addEventListener("click", () => runOpenAIAction("generate_quiz"));
        document.getElementById("exportRiseBtn").addEventListener("click", exportRiseLesson);
        document.getElementById("saveBtn").addEventListener("click", saveDraft);
        document.getElementById("commitBtn").addEventListener("click", commitUniversal);
        document.getElementById("rebuildBtn").addEventListener("click", () => runOpenAIAction("rebuild_help"));

        loadManifest();
    """),

    TEMPLATE_DIR / "README.md": dedent("""\
        # Editor Dashboard Templates

        These files are the source templates for the Arkansas Civics editor dashboard.

        The generator script copies these templates into:
        - apps/editor-dashboard/
        - netlify/functions/

        Edit templates here, not inside large Python strings.
    """),

    ROOT / "netlify.toml": dedent("""\
        [build]
          publish = "apps/editor-dashboard"
          functions = "netlify/functions"

        [[redirects]]
          from = "/api/*"
          to = "/.netlify/functions/:splat"
          status = 200
    """),

    FUNCTION_TEMPLATE_DIR / "openai-proxy.js": dedent("""\
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
    """),

    FUNCTION_TEMPLATE_DIR / "save-segment.js": dedent("""\
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
    """),

    FUNCTION_TEMPLATE_DIR / "commit-universal.js": dedent("""\
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
    """),

    FUNCTION_TEMPLATE_DIR / "chapter-context.js": dedent("""\
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
    """),

    FUNCTION_TEMPLATE_DIR / "export-rise.js": dedent("""\
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
    """),

    ROOT / "scripts" / "copy_dashboard_content.py": dedent("""\
        from pathlib import Path
        import shutil
        import json

        ROOT = Path(__file__).resolve().parents[1]
        CONTENT_SRC = ROOT / "content" / "courses"
        DASHBOARD_CONTENT = ROOT / "apps" / "editor-dashboard" / "content"

        def main():
            if DASHBOARD_CONTENT.exists():
                shutil.rmtree(DASHBOARD_CONTENT)

            DASHBOARD_CONTENT.mkdir(parents=True, exist_ok=True)

            manifest = {}

            for course in sorted(CONTENT_SRC.glob("course_*")):
                course_out = DASHBOARD_CONTENT / course.name
                course_out.mkdir(parents=True, exist_ok=True)
                manifest[course.name] = {}

                for chapter in sorted(course.glob("chapter_*")):
                    chapter_out = course_out / chapter.name
                    chapter_out.mkdir(parents=True, exist_ok=True)

                    seg_out = chapter_out / "segments"
                    seg_out.mkdir(parents=True, exist_ok=True)

                    manifest[course.name][chapter.name] = []

                    src_seg_dir = chapter / "segments"
                    if not src_seg_dir.exists():
                        continue

                    for seg in sorted(src_seg_dir.glob("*.md")):
                        dst = seg_out / seg.name
                        shutil.copy2(seg, dst)
                        manifest[course.name][chapter.name].append(f"segments/{seg.name}")

            manifest_path = ROOT / "apps" / "editor-dashboard" / "content-manifest.json"
            manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")

            print("\\nDashboard content copied.")
            print(f"Manifest written to: {manifest_path}")
            print(f"Content copied to: {DASHBOARD_CONTENT}")

        if __name__ == "__main__":
            main()
    """),

    ROOT / "scripts" / "export_rise_course.py": dedent("""\
        import json
        import sys
        from pathlib import Path

        ROOT = Path(__file__).resolve().parents[1]
        EXPORT_DIR = ROOT / "exports" / "articulate" / "rise"
        EXPORT_DIR.mkdir(parents=True, exist_ok=True)

        def main():
            if len(sys.argv) < 2:
                print("Usage: python scripts/export_rise_course.py <request_json>")
                sys.exit(1)

            request_path = Path(sys.argv[1])
            if not request_path.exists():
                print("Request file not found.")
                sys.exit(1)

            body = json.loads(request_path.read_text(encoding="utf-8"))

            title = f"{body.get('course', 'course')}_{body.get('chapter', 'chapter')}_{body.get('segment', 'segment')}"
            out_path = EXPORT_DIR / f"{title}.md"

            content = []
            content.append(f"# {title}")
            content.append("")
            content.append("## Source Content")
            content.append("")
            content.append(body.get("content", ""))
            content.append("")
            content.append("## Instruction")
            content.append("")
            content.append(body.get("instruction", ""))
            content.append("")
            content.append("## Rise Block Suggestions")
            content.append("")
            content.append("- Text block")
            content.append("- Knowledge check")
            content.append("- Reflection prompt")
            content.append("- Labeled graphic or process block")
            content.append("- Scenario interaction")

            out_path.write_text("\\n".join(content), encoding="utf-8")

            print(f"Rise export written to: {out_path}")

        if __name__ == "__main__":
            main()
    """),

    ROOT / "scripts" / "editor_dashboard_generator.py": dedent("""\
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

            print("\\nEditor dashboard scaffold generated.\\n")
            print(f"Frontend: {APP_DIR}")
            print(f"Functions: {FUNCTIONS_DIR}")
            print("\\nNext steps:")
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
    """),
}


def write_file(path: Path, content: str):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def backup_existing_generator():
    if GENERATOR_PATH.exists():
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = BACKUP_DIR / f"editor_dashboard_generator_{timestamp}.py"
        shutil.copy2(GENERATOR_PATH, backup_path)
        print(f"Backed up existing generator to: {backup_path}")


def main():
    backup_existing_generator()

    for path, content in FILES.items():
        write_file(path, content)

    print("\\nDashboard architecture upgrade complete.\\n")
    print(f"Templates: {TEMPLATE_DIR}")
    print(f"Functions: {FUNCTIONS_DIR}")
    print(f"App: {APP_DIR}")
    print("\\nNext steps:")
    print("1. Run: python scripts/editor_dashboard_generator.py")
    print("2. Run: python scripts/copy_dashboard_content.py")
    print("3. Run: python scripts/build_all.py")
    print("4. Deploy dashboard to Netlify")
    print("5. Start using the Course Factory buttons")


if __name__ == "__main__":
    main()