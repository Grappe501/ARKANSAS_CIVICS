
(function() {
  const data = window.PHASE12_CONTENT || window.PHASE095_CONTENT || {};
  const courses = Array.isArray(data.courses) ? data.courses : [];

  const els = {
    searchInput: document.getElementById("searchInput"),
    courseSelect: document.getElementById("courseSelect"),
    chapterSelect: document.getElementById("chapterSelect"),
    segmentSelect: document.getElementById("segmentSelect"),
    markCompleteBtn: document.getElementById("markCompleteBtn"),
    bookmarkBtn: document.getElementById("bookmarkBtn"),
    resumeBtn: document.getElementById("resumeBtn"),
    clearProgressBtn: document.getElementById("clearProgressBtn"),
    searchResults: document.getElementById("searchResults"),
    searchCount: document.getElementById("searchCount"),
    bookmarkList: document.getElementById("bookmarkList"),
    bookmarkCount: document.getElementById("bookmarkCount"),
    lessonTitle: document.getElementById("lessonTitle"),
    lessonMeta: document.getElementById("lessonMeta"),
    segmentHeading: document.getElementById("segmentHeading"),
    activePath: document.getElementById("activePath"),
    segmentTags: document.getElementById("segmentTags"),
    wordCount: document.getElementById("wordCount"),
    segmentContent: document.getElementById("segmentContent"),
    segmentList: document.getElementById("segmentList"),
    courseCount: document.getElementById("courseCount"),
    chapterCount: document.getElementById("chapterCount"),
    segmentCount: document.getElementById("segmentCount"),
    completionBadge: document.getElementById("completionBadge"),

    // Added but optional; these only activate if the upgraded HTML includes them
    completionStat: document.getElementById("completionStat"),
    missionCount: document.getElementById("missionCount"),
    missionList: document.getElementById("missionList"),

    hook: document.getElementById("hook"),
    reality: document.getElementById("reality"),
    actions: document.getElementById("actions"),
    reflectionInput: document.getElementById("reflectionInput"),
    nextStep: document.getElementById("nextStep"),

    completeActionBtn: document.getElementById("completeActionBtn"),
    saveReflectionBtn: document.getElementById("saveReflectionBtn"),
    nextLessonBtn: document.getElementById("nextLessonBtn")
  };

  const storageKeys = {
    complete: "arkcivics_complete_segments_v2",
    bookmarks: "arkcivics_bookmarks_v2",
    last: "arkcivics_last_segment_v2",
    missions: "arkcivics_missions_v2",
    reflections: "arkcivics_reflections_v2",
    completedActions: "arkcivics_completed_actions_v2"
  };

  const state = {
    selectedCourse: null,
    selectedChapter: null,
    selectedSegment: null,
    completed: loadJSON(storageKeys.complete, []),
    bookmarks: loadJSON(storageKeys.bookmarks, []),
    missions: loadJSON(storageKeys.missions, []),
    reflections: loadJSON(storageKeys.reflections, {}),
    completedActions: loadJSON(storageKeys.completedActions, {}),
    searchIndex: buildSearchIndex(courses)
  };

  function loadJSON(key, fallback) {
    try {
      const parsed = JSON.parse(localStorage.getItem(key));
      return parsed == null ? fallback : parsed;
    } catch (_) {
      return fallback;
    }
  }

  function saveJSON(key, value) {
    localStorage.setItem(key, JSON.stringify(value));
  }

  function segmentId(courseSlug, chapterSlug, segmentSlug) {
    return [courseSlug, chapterSlug, segmentSlug].join("::");
  }

  function actionId(courseSlug, chapterSlug, segmentSlug, actionText) {
    return [courseSlug, chapterSlug, segmentSlug, actionText].join("::");
  }

  function buildSearchIndex(courseList) {
    const rows = [];
    courseList.forEach(course => {
      (course.chapters || []).forEach(chapter => {
        (chapter.segments || []).forEach(segment => {
          const activationText = [
            segment.hook || "",
            segment.reality || "",
            Array.isArray(segment.actions) ? segment.actions.join(" ") : "",
            segment.reflection || "",
            segment.next_step || segment.next || ""
          ].join(" ");

          rows.push({
            id: segmentId(course.slug, chapter.slug, segment.slug),
            courseSlug: course.slug,
            chapterSlug: chapter.slug,
            segmentSlug: segment.slug,
            courseTitle: course.title,
            chapterTitle: chapter.title,
            segmentTitle: segment.title,
            tags: segment.tags || [],
            preview: segment.preview || "",
            format: detectSegmentFormat(segment),
            haystack: [
              course.title,
              chapter.title,
              segment.title,
              segment.content || "",
              activationText,
              (segment.tags || []).join(" ")
            ].join(" ").toLowerCase()
          });
        });
      });
    });
    return rows;
  }

  function detectSegmentFormat(segment) {
    if (!segment || typeof segment !== "object") return "unknown";
    if (segment.hook || segment.reality || segment.actions || segment.reflection || segment.next_step || segment.next) {
      return "activation";
    }
    if (segment.content) return "markdown";
    return "unknown";
  }

  function renderMarkdown(md) {
    const escape = (s) => String(s)
      .replaceAll("&", "&amp;")
      .replaceAll("<", "&lt;")
      .replaceAll(">", "&gt;");
    const lines = String(md || "").replace(/\r\n/g, "\n").split("\n");
    let html = "";
    let inList = false;

    const closeList = () => {
      if (inList) {
        html += "</ul>";
        inList = false;
      }
    };

    for (const rawLine of lines) {
      const line = rawLine.trimEnd();

      if (!line.trim()) {
        closeList();
        continue;
      }
      if (line.startsWith("### ")) {
        closeList();
        html += `<h3>${escape(line.slice(4))}</h3>`;
      } else if (line.startsWith("## ")) {
        closeList();
        html += `<h2>${escape(line.slice(3))}</h2>`;
      } else if (line.startsWith("# ")) {
        closeList();
        html += `<h1>${escape(line.slice(2))}</h1>`;
      } else if (line.startsWith("- ")) {
        if (!inList) {
          html += "<ul>";
          inList = true;
        }
        html += `<li>${escape(line.slice(2))}</li>`;
      } else if (/^---+$/.test(line.trim())) {
        closeList();
        html += "<hr />";
      } else {
        closeList();
        html += `<p>${escape(line)}</p>`;
      }
    }
    closeList();
    return html || "<p>No content available for this segment yet.</p>";
  }

  function currentCourse() {
    return courses.find(c => c.slug === state.selectedCourse) || courses[0] || null;
  }

  function currentChapter() {
    const course = currentCourse();
    if (!course) return null;
    return (course.chapters || []).find(c => c.slug === state.selectedChapter) || (course.chapters || [])[0] || null;
  }

  function currentSegment() {
    const chapter = currentChapter();
    if (!chapter) return null;
    return (chapter.segments || []).find(s => s.slug === state.selectedSegment) || (chapter.segments || [])[0] || null;
  }

  function updateTopStats() {
    els.courseCount.textContent = data.course_count || courses.length || 0;
    els.chapterCount.textContent = data.chapter_count || courses.reduce((n, c) => n + (c.chapters || []).length, 0);
    const totalSegments = data.segment_count || courses.reduce((n, c) => n + (c.chapters || []).reduce((m, ch) => m + (ch.segments || []).length, 0), 0);
    els.segmentCount.textContent = totalSegments;

    const pct = totalSegments ? Math.round((state.completed.length / totalSegments) * 100) : 0;
    if (els.completionBadge) {
      els.completionBadge.textContent = `${pct}%`;
    }
    if (els.completionStat) {
      els.completionStat.textContent = state.completed.length;
    }
    if (els.missionCount) {
      els.missionCount.textContent = `Missions: ${state.missions.length}`;
    }
  }

  function fillCourses() {
    els.courseSelect.innerHTML = "";
    courses.forEach(course => {
      const opt = document.createElement("option");
      opt.value = course.slug;
      opt.textContent = course.title;
      els.courseSelect.appendChild(opt);
    });
    if (!state.selectedCourse && courses[0]) {
      state.selectedCourse = courses[0].slug;
    }
    els.courseSelect.value = state.selectedCourse || "";
  }

  function fillChapters() {
    const course = currentCourse();
    els.chapterSelect.innerHTML = "";
    const chapters = (course && course.chapters) || [];
    chapters.forEach(chapter => {
      const opt = document.createElement("option");
      opt.value = chapter.slug;
      opt.textContent = chapter.title;
      els.chapterSelect.appendChild(opt);
    });
    if (!chapters.find(c => c.slug === state.selectedChapter) && chapters[0]) {
      state.selectedChapter = chapters[0].slug;
    }
    els.chapterSelect.value = state.selectedChapter || "";
  }

  function fillSegments() {
    const chapter = currentChapter();
    els.segmentSelect.innerHTML = "";
    const segments = (chapter && chapter.segments) || [];
    segments.forEach(segment => {
      const opt = document.createElement("option");
      opt.value = segment.slug;
      opt.textContent = segment.title;
      els.segmentSelect.appendChild(opt);
    });
    if (!segments.find(s => s.slug === state.selectedSegment) && segments[0]) {
      state.selectedSegment = segments[0].slug;
    }
    els.segmentSelect.value = state.selectedSegment || "";
  }

  function renderNavigator() {
    const chapter = currentChapter();
    const course = currentCourse();
    const segments = (chapter && chapter.segments) || [];
    const activeId = course && chapter ? segmentId(course.slug, chapter.slug, state.selectedSegment) : null;

    els.segmentList.innerHTML = "";
    if (!segments.length) {
      els.segmentList.innerHTML = '<div class="muted">No segments found in this chapter.</div>';
      return;
    }

    segments.forEach(segment => {
      const btn = document.createElement("button");
      const segId = segmentId(course.slug, chapter.slug, segment.slug);
      const completed = state.completed.includes(segId);
      const format = detectSegmentFormat(segment);

      btn.className = "segment-item" + (activeId === segId ? " active" : "") + (completed ? " completed" : "");
      btn.innerHTML =
        `<div class="segment-title">${segment.title}</div>` +
        `<small>${segment.word_count || 0} words${format === "activation" ? " • activation" : ""}${completed ? " • completed" : ""}</small>`;
      btn.addEventListener("click", () => {
        state.selectedSegment = segment.slug;
        sync();
      });
      els.segmentList.appendChild(btn);
    });
  }

  function renderBookmarks() {
    if (els.bookmarkCount) {
      els.bookmarkCount.textContent = state.bookmarks.length;
    }
    els.bookmarkList.innerHTML = "";
    if (!state.bookmarks.length) {
      els.bookmarkList.className = "results empty";
      els.bookmarkList.textContent = "No bookmarks yet.";
      return;
    }
    els.bookmarkList.className = "results";
    state.bookmarks.forEach(item => {
      const btn = document.createElement("button");
      btn.className = "bookmark-item";
      btn.innerHTML = `<strong>${item.segmentTitle}</strong><small>${item.courseTitle} → ${item.chapterTitle}</small>`;
      btn.addEventListener("click", () => {
        state.selectedCourse = item.courseSlug;
        state.selectedChapter = item.chapterSlug;
        state.selectedSegment = item.segmentSlug;
        sync();
      });
      els.bookmarkList.appendChild(btn);
    });
  }

  function renderSearchResults(query) {
    const q = String(query || "").trim().toLowerCase();
    if (!q) {
      if (els.searchCount) {
        els.searchCount.textContent = "0";
      }
      els.searchResults.className = "results empty";
      els.searchResults.textContent = "Start typing to search the course library.";
      return;
    }

    const matches = state.searchIndex.filter(row => row.haystack.includes(q)).slice(0, 50);
    if (els.searchCount) {
      els.searchCount.textContent = String(matches.length);
    }
    els.searchResults.innerHTML = "";
    els.searchResults.className = "results";

    if (!matches.length) {
      els.searchResults.className = "results empty";
      els.searchResults.textContent = "No matches found.";
      return;
    }

    matches.forEach(row => {
      const btn = document.createElement("button");
      btn.className = "result-item";
      btn.innerHTML = `<strong>${row.segmentTitle}</strong><small>${row.courseTitle} → ${row.chapterTitle}${row.format === "activation" ? " • activation" : ""}</small>`;
      btn.addEventListener("click", () => {
        state.selectedCourse = row.courseSlug;
        state.selectedChapter = row.chapterSlug;
        state.selectedSegment = row.segmentSlug;
        sync();
      });
      els.searchResults.appendChild(btn);
    });
  }

  function hideActivationPanels() {
    if (els.hook && els.hook.parentElement) els.hook.parentElement.style.display = "none";
    if (els.reality && els.reality.parentElement) els.reality.parentElement.style.display = "none";
    if (els.actions && els.actions.parentElement) els.actions.parentElement.style.display = "none";
    if (els.reflectionInput && els.reflectionInput.parentElement) els.reflectionInput.parentElement.style.display = "none";
    if (els.nextStep && els.nextStep.parentElement) els.nextStep.parentElement.style.display = "none";
  }

  function showActivationPanels() {
    if (els.hook && els.hook.parentElement) els.hook.parentElement.style.display = "";
    if (els.reality && els.reality.parentElement) els.reality.parentElement.style.display = "";
    if (els.actions && els.actions.parentElement) els.actions.parentElement.style.display = "";
    if (els.reflectionInput && els.reflectionInput.parentElement) els.reflectionInput.parentElement.style.display = "";
    if (els.nextStep && els.nextStep.parentElement) els.nextStep.parentElement.style.display = "";
  }

  function clearActivationPanels() {
    if (els.hook) els.hook.textContent = "";
    if (els.reality) els.reality.textContent = "";
    if (els.actions) els.actions.innerHTML = "";
    if (els.reflectionInput) els.reflectionInput.value = "";
    if (els.nextStep) els.nextStep.textContent = "";
  }

  function renderActivationSegment(segment, course, chapter, id) {
    showActivationPanels();

    if (els.segmentContent) {
      els.segmentContent.style.display = "none";
      els.segmentContent.innerHTML = "";
    }

    if (els.hook) {
      els.hook.textContent = segment.hook || "";
    }
    if (els.reality) {
      els.reality.textContent = segment.reality || "";
    }

    if (els.actions) {
      els.actions.innerHTML = "";
      const items = Array.isArray(segment.actions) ? segment.actions : [];
      if (!items.length) {
        const li = document.createElement("li");
        li.textContent = "No actions available for this lesson yet.";
        els.actions.appendChild(li);
      } else {
        items.forEach(actionText => {
          const li = document.createElement("li");
          const checkbox = document.createElement("input");
          checkbox.type = "checkbox";
          checkbox.className = "action-checkbox";
          checkbox.dataset.actionId = actionId(course.slug, chapter.slug, segment.slug, actionText);
          checkbox.checked = !!state.completedActions[checkbox.dataset.actionId];

          const label = document.createElement("label");
          label.textContent = actionText;

          checkbox.addEventListener("change", (event) => {
            const id = event.target.dataset.actionId;
            if (event.target.checked) {
              state.completedActions[id] = true;
            } else {
              delete state.completedActions[id];
            }
            saveJSON(storageKeys.completedActions, state.completedActions);
          });

          li.appendChild(checkbox);
          li.appendChild(label);
          els.actions.appendChild(li);
        });
      }
    }

    if (els.reflectionInput) {
      els.reflectionInput.value = state.reflections[id]?.text || "";
      els.reflectionInput.placeholder = segment.reflection || "Write your reflection here...";
    }

    if (els.nextStep) {
      els.nextStep.textContent = segment.next_step || segment.next || "";
    }

    if (els.completeActionBtn) {
      const missionAlreadyLogged = state.missions.some(m => m.segmentId === id);
      els.completeActionBtn.disabled = missionAlreadyLogged;
      els.completeActionBtn.textContent = missionAlreadyLogged ? "Mission Logged" : "I Did This";
    }

    if (els.saveReflectionBtn) {
      els.saveReflectionBtn.textContent = "Save Reflection";
      els.saveReflectionBtn.disabled = false;
    }

    if (els.nextLessonBtn) {
      els.nextLessonBtn.disabled = !hasNextLesson();
    }
  }

  function renderClassicSegment(segment) {
    hideActivationPanels();

    if (els.segmentContent) {
      els.segmentContent.style.display = "block";
      els.segmentContent.innerHTML = renderMarkdown(segment.content || "");
    }
  }

  function renderReader() {
    const course = currentCourse();
    const chapter = currentChapter();
    const segment = currentSegment();

    if (!course || !chapter || !segment) {
      els.lessonTitle.textContent = "No course data found";
      els.lessonMeta.textContent = "Run the Phase 09.5 build script to generate the content bundle.";
      els.segmentHeading.textContent = "Content unavailable";
      els.activePath.textContent = "";
      if (els.segmentTags) els.segmentTags.innerHTML = "";
      if (els.wordCount) els.wordCount.textContent = "";
      if (els.segmentContent) {
        els.segmentContent.style.display = "block";
        els.segmentContent.innerHTML = "<p>No segment content is available yet.</p>";
      }
      clearActivationPanels();
      hideActivationPanels();
      return;
    }

    const id = segmentId(course.slug, chapter.slug, segment.slug);
    const format = detectSegmentFormat(segment);

    els.lessonTitle.textContent = course.title;
    els.lessonMeta.textContent = chapter.title;
    els.segmentHeading.textContent = segment.title;
    els.activePath.textContent = `${course.title} → ${chapter.title} → ${segment.title}`;
    if (els.wordCount) {
      els.wordCount.textContent = `${segment.word_count || 0} words`;
    }
    if (els.segmentTags) {
      els.segmentTags.innerHTML = (segment.tags || []).map(tag => `<span class="tag">${tag}</span>`).join("");
    }

    saveJSON(storageKeys.last, {
      courseSlug: course.slug,
      chapterSlug: chapter.slug,
      segmentSlug: segment.slug
    });

    if (format === "activation") {
      renderActivationSegment(segment, course, chapter, id);
    } else {
      renderClassicSegment(segment);
    }

    if (state.completed.includes(id)) {
      els.markCompleteBtn.textContent = "Completed";
      els.markCompleteBtn.disabled = true;
    } else {
      els.markCompleteBtn.textContent = "Mark complete";
      els.markCompleteBtn.disabled = false;
    }
  }

  function renderMissionLog() {
    if (!els.missionList) return;

    els.missionList.innerHTML = "";
    if (!state.missions.length) {
      const li = document.createElement("li");
      li.textContent = "No missions logged yet.";
      els.missionList.appendChild(li);
      return;
    }

    state.missions
      .slice()
      .sort((a, b) => b.completedAt - a.completedAt)
      .forEach(mission => {
        const li = document.createElement("li");
        const date = new Date(mission.completedAt);
        li.innerHTML = `<strong>${mission.title}</strong><small>${mission.courseTitle} → ${mission.chapterTitle} • ${date.toLocaleString()}</small>`;
        els.missionList.appendChild(li);
      });
  }

  function sync() {
    fillCourses();
    fillChapters();
    fillSegments();
    renderReader();
    renderNavigator();
    renderBookmarks();
    renderMissionLog();
    updateTopStats();
    renderSearchResults(els.searchInput ? els.searchInput.value : "");
  }

  function addBookmark() {
    const course = currentCourse();
    const chapter = currentChapter();
    const segment = currentSegment();
    if (!course || !chapter || !segment) return;
    const id = segmentId(course.slug, chapter.slug, segment.slug);
    if (state.bookmarks.some(b => b.id === id)) return;

    state.bookmarks.unshift({
      id,
      courseSlug: course.slug,
      chapterSlug: chapter.slug,
      segmentSlug: segment.slug,
      courseTitle: course.title,
      chapterTitle: chapter.title,
      segmentTitle: segment.title
    });
    saveJSON(storageKeys.bookmarks, state.bookmarks);
    renderBookmarks();
    updateTopStats();
  }

  function markComplete() {
    const course = currentCourse();
    const chapter = currentChapter();
    const segment = currentSegment();
    if (!course || !chapter || !segment) return;
    const id = segmentId(course.slug, chapter.slug, segment.slug);
    if (!state.completed.includes(id)) {
      state.completed.push(id);
      saveJSON(storageKeys.complete, state.completed);
    }
    updateTopStats();
    renderReader();
    renderNavigator();
  }

  function completeActivationMission() {
    const course = currentCourse();
    const chapter = currentChapter();
    const segment = currentSegment();
    if (!course || !chapter || !segment) return;

    const id = segmentId(course.slug, chapter.slug, segment.slug);
    const alreadyLogged = state.missions.some(m => m.segmentId === id);
    if (!alreadyLogged) {
      state.missions.push({
        segmentId: id,
        title: segment.title,
        courseTitle: course.title,
        chapterTitle: chapter.title,
        completedAt: Date.now()
      });
      saveJSON(storageKeys.missions, state.missions);
    }

    if (!state.completed.includes(id)) {
      state.completed.push(id);
      saveJSON(storageKeys.complete, state.completed);
    }

    renderMissionLog();
    updateTopStats();
    renderReader();
    renderNavigator();
  }

  function saveReflection() {
    const course = currentCourse();
    const chapter = currentChapter();
    const segment = currentSegment();
    if (!course || !chapter || !segment || !els.reflectionInput) return;

    const id = segmentId(course.slug, chapter.slug, segment.slug);
    state.reflections[id] = {
      text: els.reflectionInput.value,
      updatedAt: Date.now()
    };
    saveJSON(storageKeys.reflections, state.reflections);
  }

  function hasNextLesson() {
    const chapter = currentChapter();
    const segments = (chapter && chapter.segments) || [];
    const currentIndex = segments.findIndex(s => s.slug === state.selectedSegment);
    return currentIndex > -1 && currentIndex < segments.length - 1;
  }

  function goToNextLesson() {
    const chapter = currentChapter();
    const segments = (chapter && chapter.segments) || [];
    const currentIndex = segments.findIndex(s => s.slug === state.selectedSegment);

    if (currentIndex > -1 && currentIndex < segments.length - 1) {
      state.selectedSegment = segments[currentIndex + 1].slug;
      sync();
      return;
    }

    const course = currentCourse();
    const chapters = (course && course.chapters) || [];
    const chapterIndex = chapters.findIndex(ch => ch.slug === state.selectedChapter);
    if (chapterIndex > -1 && chapterIndex < chapters.length - 1) {
      state.selectedChapter = chapters[chapterIndex + 1].slug;
      state.selectedSegment = null;
      sync();
    }
  }

  function resumeLast() {
    const last = loadJSON(storageKeys.last, null);
    if (!last) return;
    state.selectedCourse = last.courseSlug;
    state.selectedChapter = last.chapterSlug;
    state.selectedSegment = last.segmentSlug;
    sync();
  }

  function clearProgress() {
    localStorage.removeItem(storageKeys.complete);
    localStorage.removeItem(storageKeys.bookmarks);
    localStorage.removeItem(storageKeys.last);
    localStorage.removeItem(storageKeys.missions);
    localStorage.removeItem(storageKeys.reflections);
    localStorage.removeItem(storageKeys.completedActions);

    state.completed = [];
    state.bookmarks = [];
    state.missions = [];
    state.reflections = {};
    state.completedActions = {};
    sync();
  }

  function bindEvents() {
    els.courseSelect.addEventListener("change", () => {
      state.selectedCourse = els.courseSelect.value;
      state.selectedChapter = null;
      state.selectedSegment = null;
      sync();
    });

    els.chapterSelect.addEventListener("change", () => {
      state.selectedChapter = els.chapterSelect.value;
      state.selectedSegment = null;
      sync();
    });

    els.segmentSelect.addEventListener("change", () => {
      state.selectedSegment = els.segmentSelect.value;
      sync();
    });

    if (els.searchInput) {
      els.searchInput.addEventListener("input", (e) => renderSearchResults(e.target.value));
    }

    if (els.bookmarkBtn) {
      els.bookmarkBtn.addEventListener("click", addBookmark);
    }

    if (els.markCompleteBtn) {
      els.markCompleteBtn.addEventListener("click", markComplete);
    }

    if (els.resumeBtn) {
      els.resumeBtn.addEventListener("click", resumeLast);
    }

    if (els.clearProgressBtn) {
      els.clearProgressBtn.addEventListener("click", clearProgress);
    }

    if (els.completeActionBtn) {
      els.completeActionBtn.addEventListener("click", completeActivationMission);
    }

    if (els.saveReflectionBtn) {
      els.saveReflectionBtn.addEventListener("click", saveReflection);
    }

    if (els.nextLessonBtn) {
      els.nextLessonBtn.addEventListener("click", goToNextLesson);
    }
  }

  function boot() {
    if (!courses.length) {
      renderReader();
      return;
    }

    const last = loadJSON(storageKeys.last, null);
    if (last) {
      state.selectedCourse = last.courseSlug;
      state.selectedChapter = last.chapterSlug;
      state.selectedSegment = last.segmentSlug;
    } else {
      state.selectedCourse = courses[0].slug;
    }

    bindEvents();
    sync();
  }

  boot();
})();
