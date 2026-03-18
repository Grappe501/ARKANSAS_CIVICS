(() => {
  "use strict";

  const INDEX_URL = "../../exports/lesson_player/lesson_player_index.json";
  const RUNTIME_URL = "../../exports/learning_runtime/learning_runtime_snapshot.json";
  const IDLE_LIMIT_SECONDS = 90;
  const STORAGE_KEY = "standup-arkansas-lesson-player";

  const state = {
    index: null,
    runtimeSnapshot: null,
    selectedCourseSlug: null,
    selectedLessonSlug: null,
    selectedSegmentName: null,
    searchQuery: "",
    isRunning: false,
    sessionActiveSeconds: 0,
    sessionIdleSeconds: 0,
    totalSegmentSeconds: 0,
    completedSegments: new Set(),
    lastInteractionAt: Date.now(),
    timerHandle: null,
  };

  const refs = {};

  function $(id) {
    return document.getElementById(id);
  }

  function safeArray(value) {
    return Array.isArray(value) ? value : [];
  }

  function normalizeSearch(value) {
    return String(value || "").trim().toLowerCase();
  }

  function fmtDuration(seconds) {
    const value = Math.max(0, Number(seconds || 0));
    const hours = Math.floor(value / 3600).toString().padStart(2, "0");
    const minutes = Math.floor((value % 3600) / 60).toString().padStart(2, "0");
    const secs = Math.floor(value % 60).toString().padStart(2, "0");
    return `${hours}:${minutes}:${secs}`;
  }

  function saveLocalState() {
    const payload = {
      selectedCourseSlug: state.selectedCourseSlug,
      selectedLessonSlug: state.selectedLessonSlug,
      selectedSegmentName: state.selectedSegmentName,
      sessionActiveSeconds: state.sessionActiveSeconds,
      sessionIdleSeconds: state.sessionIdleSeconds,
      totalSegmentSeconds: state.totalSegmentSeconds,
      completedSegments: [...state.completedSegments],
    };
    localStorage.setItem(STORAGE_KEY, JSON.stringify(payload));
  }

  function loadLocalState() {
    try {
      const raw = localStorage.getItem(STORAGE_KEY);
      if (!raw) return;
      const payload = JSON.parse(raw);
      state.selectedCourseSlug = payload.selectedCourseSlug || null;
      state.selectedLessonSlug = payload.selectedLessonSlug || null;
      state.selectedSegmentName = payload.selectedSegmentName || null;
      state.sessionActiveSeconds = Number(payload.sessionActiveSeconds || 0);
      state.sessionIdleSeconds = Number(payload.sessionIdleSeconds || 0);
      state.totalSegmentSeconds = Number(payload.totalSegmentSeconds || 0);
      state.completedSegments = new Set(safeArray(payload.completedSegments));
    } catch (error) {
      console.error(error);
    }
  }

  async function fetchJson(url) {
    const response = await fetch(url, { cache: "no-store" });
    if (!response.ok) throw new Error(`Failed to load ${url} (${response.status})`);
    return response.json();
  }

  async function loadData() {
    bindRefs();
    loadLocalState();
    wireRuntimeControls();
    wireActivitySensors();

    try {
      state.index = await fetchJson(INDEX_URL);
    } catch (error) {
      renderError(`Unable to load lesson player index. ${error.message}`);
      return;
    }

    try {
      state.runtimeSnapshot = await fetchJson(RUNTIME_URL);
    } catch (error) {
      console.warn(error);
    }

    seedSelection();
    render();
  }

  function bindRefs() {
    refs.nav = $("lesson-player-nav");
    refs.search = $("lessonPlayerSearch");
    refs.breadcrumb = $("lesson-player-breadcrumb");
    refs.title = $("lesson-player-title");
    refs.summary = $("lesson-player-summary");
    refs.meta = $("lesson-player-meta");
    refs.objectives = $("lesson-player-objectives");
    refs.practice = $("lesson-player-practice");
    refs.content = $("lesson-player-content");
    refs.clock = $("lesson-clock-display");
    refs.clockStatus = $("lesson-clock-status");
    refs.runtimeStats = $("lesson-runtime-stats");
    refs.prev = $("lessonPrevBtn");
    refs.next = $("lessonNextBtn");
    refs.start = $("lessonStartBtn");
    refs.pause = $("lessonPauseBtn");
    refs.complete = $("lessonCompleteBtn");

    refs.search?.addEventListener("input", (event) => {
      state.searchQuery = event.target.value || "";
      renderNav();
    });
  }

  function wireRuntimeControls() {
    refs.start?.addEventListener("click", startSession);
    refs.pause?.addEventListener("click", pauseSession);
    refs.complete?.addEventListener("click", completeSegment);
    refs.prev?.addEventListener("click", goPrevious);
    refs.next?.addEventListener("click", goNext);
  }

  function wireActivitySensors() {
    const markActive = () => {
      state.lastInteractionAt = Date.now();
    };

    ["mousemove", "keydown", "scroll", "click", "touchstart"].forEach((eventName) => {
      window.addEventListener(eventName, markActive, { passive: true });
    });
  }

  function getCourses() {
    return safeArray(state.index?.courses);
  }

  function getSelectedCourse() {
    return getCourses().find((course) => course.slug === state.selectedCourseSlug) || null;
  }

  function getSelectedLesson() {
    const course = getSelectedCourse();
    return safeArray(course?.lessons).find((lesson) => lesson.slug === state.selectedLessonSlug) || null;
  }

  function getSelectedSegment() {
    const lesson = getSelectedLesson();
    return safeArray(lesson?.segments).find((segment) => segment.segment_name === state.selectedSegmentName) || null;
  }

  function seedSelection() {
    const courses = getCourses();
    if (!courses.length) return;

    const course = courses.find((item) => item.slug === state.selectedCourseSlug) || courses[0];
    state.selectedCourseSlug = course.slug;

    const lessons = safeArray(course.lessons);
    const lesson = lessons.find((item) => item.slug === state.selectedLessonSlug) || lessons[0];
    state.selectedLessonSlug = lesson?.slug || null;

    const segments = safeArray(lesson?.segments);
    const segment = segments.find((item) => item.segment_name === state.selectedSegmentName) || segments[0];
    state.selectedSegmentName = segment?.segment_name || null;
  }

  function render() {
    renderNav();
    renderDetail();
    renderRuntime();
    saveLocalState();
  }

  function renderError(message) {
    if (refs.nav) refs.nav.textContent = message;
    if (refs.content) refs.content.textContent = message;
  }

  function renderNav() {
    if (!refs.nav) return;
    refs.nav.innerHTML = "";

    const query = normalizeSearch(state.searchQuery);

    getCourses().forEach((course) => {
      const courseHaystack = normalizeSearch(`${course.slug} ${course.title}`);
      const lessonMatches = safeArray(course.lessons).filter((lesson) => {
        const lessonHaystack = normalizeSearch(`${lesson.slug} ${lesson.title}`);
        const segmentMatches = safeArray(lesson.segments).some((segment) => {
          const segmentHaystack = normalizeSearch(`${segment.segment_name} ${segment.segment_title} ${segment.summary}`);
          return !query || segmentHaystack.includes(query);
        });
        return !query || lessonHaystack.includes(query) || segmentMatches;
      });

      const courseVisible = !query || courseHaystack.includes(query) || lessonMatches.length > 0;
      if (!courseVisible) return;

      const courseBlock = document.createElement("div");
      courseBlock.className = "lesson-nav-course";

      const courseTitle = document.createElement("button");
      courseTitle.type = "button";
      courseTitle.className = "lesson-nav-course-title";
      courseTitle.textContent = `${course.title} (${course.lesson_count} lessons)`;
      courseTitle.addEventListener("click", () => {
        state.selectedCourseSlug = course.slug;
        const firstLesson = safeArray(course.lessons)[0];
        state.selectedLessonSlug = firstLesson?.slug || null;
        state.selectedSegmentName = safeArray(firstLesson?.segments)[0]?.segment_name || null;
        resetSessionClock();
        render();
      });
      courseBlock.appendChild(courseTitle);

      lessonMatches.forEach((lesson) => {
        const lessonBlock = document.createElement("div");
        lessonBlock.className = "lesson-nav-lesson";

        const lessonTitle = document.createElement("button");
        lessonTitle.type = "button";
        lessonTitle.className = "lesson-nav-lesson-title";
        lessonTitle.textContent = lesson.title;
        lessonTitle.addEventListener("click", () => {
          state.selectedCourseSlug = course.slug;
          state.selectedLessonSlug = lesson.slug;
          state.selectedSegmentName = safeArray(lesson.segments)[0]?.segment_name || null;
          resetSessionClock();
          render();
        });
        lessonBlock.appendChild(lessonTitle);

        const segmentList = document.createElement("div");
        segmentList.className = "lesson-nav-segments";

        safeArray(lesson.segments).forEach((segment) => {
          const segmentHaystack = normalizeSearch(`${segment.segment_name} ${segment.segment_title} ${segment.summary}`);
          if (query && !segmentHaystack.includes(query) && !normalizeSearch(`${lesson.slug} ${lesson.title}`).includes(query)) {
            return;
          }

          const segmentBtn = document.createElement("button");
          segmentBtn.type = "button";
          segmentBtn.className = "lesson-nav-segment";
          if (course.slug === state.selectedCourseSlug && lesson.slug === state.selectedLessonSlug && segment.segment_name === state.selectedSegmentName) {
            segmentBtn.classList.add("active");
          }
          if (state.completedSegments.has(segmentKey(course.slug, lesson.slug, segment.segment_name))) {
            segmentBtn.classList.add("completed");
          }

          segmentBtn.innerHTML = `<span>${segment.segment_title}</span><small>${segment.estimated_minutes} min</small>`;
          segmentBtn.addEventListener("click", () => {
            loadSelection({
              courseSlug: course.slug,
              lessonSlug: lesson.slug,
              segmentName: segment.segment_name,
            });
          });
          segmentList.appendChild(segmentBtn);
        });

        lessonBlock.appendChild(segmentList);
        courseBlock.appendChild(lessonBlock);
      });

      refs.nav.appendChild(courseBlock);
    });
  }

  async function renderDetail() {
    const course = getSelectedCourse();
    const lesson = getSelectedLesson();
    const segment = getSelectedSegment();

    if (!course || !lesson || !segment) {
      refs.title.textContent = "Select a lesson segment to begin.";
      refs.summary.textContent = "The lesson player will render real content from the Arkansas courses.";
      refs.content.textContent = "No lesson selected.";
      refs.objectives.innerHTML = "";
      refs.practice.innerHTML = "";
      return;
    }

    refs.breadcrumb.textContent = `${course.title} / ${lesson.title} / ${segment.segment_title}`;
    refs.title.textContent = segment.segment_title;
    refs.summary.textContent = segment.summary || "No summary available.";

    refs.meta.innerHTML = "";
    [
      `Type: ${segment.block_type}`,
      `${segment.estimated_minutes} min`,
      `Objectives: ${lesson.objective_count}`,
      `Activities: ${lesson.activity_count}`,
      `Assessments: ${lesson.assessment_count}`,
    ].forEach((label) => {
      const chip = document.createElement("span");
      chip.className = "course-engine-chip";
      chip.textContent = label;
      refs.meta.appendChild(chip);
    });

    refs.objectives.innerHTML = "";
    const objectiveList = document.createElement("ul");
    objectiveList.className = "course-engine-bullets";
    objectiveList.innerHTML = `<li>Understand the segment’s civic purpose in the Arkansas context.</li>`;
    refs.objectives.appendChild(objectiveList);

    refs.practice.innerHTML = "";
    const practiceCard = document.createElement("div");
    practiceCard.className = "course-engine-panel";
    practiceCard.innerHTML = `
      <div class="course-engine-panel-title">Mission Prompt</div>
      <div class="course-engine-panel-text">After reading this segment, identify one real-world Arkansas action, campaign step, or public question that this lesson should prepare a learner to handle.</div>
      <div class="course-engine-panel-meta">This will later connect to quizzes, reflection prompts, and certification checkpoints.</div>
    `;
    refs.practice.appendChild(practiceCard);

    try {
      const response = await fetch(segment.dashboard_content_path, { cache: "no-store" });
      if (!response.ok) throw new Error(`Failed to load segment content (${response.status})`);
      const content = await response.text();
      refs.content.textContent = content;

      const dashboardPath = document.getElementById("activePath");
      if (dashboardPath) {
        dashboardPath.textContent = segment.dashboard_content_path;
      }
    } catch (error) {
      console.error(error);
      refs.content.textContent = `Unable to load lesson content. ${error.message}`;
    }
  }

  function renderRuntime() {
    if (!refs.clock || !refs.clockStatus || !refs.runtimeStats) return;

    refs.clock.textContent = fmtDuration(state.sessionActiveSeconds);
    refs.clockStatus.textContent = state.isRunning ? "Active Learning" : "Idle";
    refs.clockStatus.classList.toggle("active", state.isRunning);

    const course = getSelectedCourse();
    const lesson = getSelectedLesson();
    const segment = getSelectedSegment();
    const completedKey = course && lesson && segment ? segmentKey(course.slug, lesson.slug, segment.segment_name) : null;

    refs.runtimeStats.innerHTML = `
      <div class="lesson-runtime-stat"><span>Session Active</span><strong>${fmtDuration(state.sessionActiveSeconds)}</strong></div>
      <div class="lesson-runtime-stat"><span>Session Idle</span><strong>${fmtDuration(state.sessionIdleSeconds)}</strong></div>
      <div class="lesson-runtime-stat"><span>This Segment</span><strong>${fmtDuration(state.totalSegmentSeconds)}</strong></div>
      <div class="lesson-runtime-stat"><span>Completed</span><strong>${completedKey && state.completedSegments.has(completedKey) ? "Yes" : "No"}</strong></div>
    `;
  }

  function startSession() {
    if (!getSelectedSegment()) return;
    state.isRunning = true;
    state.lastInteractionAt = Date.now();

    if (state.timerHandle) window.clearInterval(state.timerHandle);
    state.timerHandle = window.setInterval(tick, 1000);
    renderRuntime();
    saveLocalState();
  }

  function pauseSession() {
    state.isRunning = false;
    if (state.timerHandle) {
      window.clearInterval(state.timerHandle);
      state.timerHandle = null;
    }
    renderRuntime();
    saveLocalState();
  }

  function resetSessionClock() {
    pauseSession();
    state.sessionActiveSeconds = 0;
    state.sessionIdleSeconds = 0;
    state.totalSegmentSeconds = 0;
    renderRuntime();
  }

  function tick() {
    const idleFor = Math.floor((Date.now() - state.lastInteractionAt) / 1000);

    if (idleFor >= IDLE_LIMIT_SECONDS) {
      state.sessionIdleSeconds += 1;
      state.isRunning = false;
      refs.clockStatus.textContent = "Paused for Inactivity";
      refs.clockStatus.classList.remove("active");
      saveLocalState();
      renderRuntime();
      return;
    }

    state.isRunning = true;
    state.sessionActiveSeconds += 1;
    state.totalSegmentSeconds += 1;
    renderRuntime();
    saveLocalState();
  }

  function segmentKey(courseSlug, lessonSlug, segmentName) {
    return `${courseSlug}/${lessonSlug}/${segmentName}`;
  }

  function completeSegment() {
    const course = getSelectedCourse();
    const lesson = getSelectedLesson();
    const segment = getSelectedSegment();
    if (!course || !lesson || !segment) return;

    state.completedSegments.add(segmentKey(course.slug, lesson.slug, segment.segment_name));
    pauseSession();
    render();
  }

  function goPrevious() {
    const lesson = getSelectedLesson();
    const segment = getSelectedSegment();
    if (!lesson || !segment || !segment.previous_segment) return;
    loadSelection({
      courseSlug: state.selectedCourseSlug,
      lessonSlug: state.selectedLessonSlug,
      segmentName: segment.previous_segment,
    });
  }

  function goNext() {
    const lesson = getSelectedLesson();
    const segment = getSelectedSegment();
    if (!lesson || !segment) return;

    if (segment.next_segment) {
      loadSelection({
        courseSlug: state.selectedCourseSlug,
        lessonSlug: state.selectedLessonSlug,
        segmentName: segment.next_segment,
      });
      return;
    }

    const course = getSelectedCourse();
    const lessons = safeArray(course?.lessons);
    const index = lessons.findIndex((item) => item.slug === lesson.slug);
    const nextLesson = index >= 0 ? lessons[index + 1] : null;

    if (nextLesson) {
      loadSelection({
        courseSlug: course.slug,
        lessonSlug: nextLesson.slug,
        segmentName: safeArray(nextLesson.segments)[0]?.segment_name,
      });
    }
  }

  function loadSelection({ courseSlug, lessonSlug, segmentName }) {
    state.selectedCourseSlug = courseSlug || state.selectedCourseSlug;
    state.selectedLessonSlug = lessonSlug || state.selectedLessonSlug;
    state.selectedSegmentName = segmentName || state.selectedSegmentName;
    resetSessionClock();
    render();

    const lessonTab = document.querySelector('[data-tab-target="lessonPlayerTab"]');
    lessonTab?.click();
  }

  function loadFromEditorSelection({ courseSlug, chapterSlug, segmentPath }) {
    const course = getCourses().find((item) => item.slug === courseSlug);
    if (!course) return;

    const lesson = safeArray(course.lessons).find((item) => item.chapter_path.includes(chapterSlug));
    if (!lesson) return;

    const fileName = String(segmentPath).replace(/^segments\//, "").replace(/\.md$/i, "");
    const segment = safeArray(lesson.segments).find((item) => item.segment_name === fileName);
    if (!segment) return;

    loadSelection({
      courseSlug,
      lessonSlug: lesson.slug,
      segmentName: segment.segment_name,
    });
  }

  window.ArkansasCivicsLessonPlayer = {
    reload: loadData,
    loadSelection,
    loadFromEditorSelection,
    getState: () => ({ ...state }),
  };

  window.addEventListener("load", loadData);
})();
