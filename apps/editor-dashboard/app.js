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
