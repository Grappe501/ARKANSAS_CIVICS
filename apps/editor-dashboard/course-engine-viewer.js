(() => {
    "use strict";
  
    // ============================================================
    // Arkansas Civics Course Engine Viewer
    // ------------------------------------------------------------
    // Purpose:
    // - Load the internal course engine index
    // - Render a browsable dashboard view of generated course packages
    // - Show lessons, objectives, blocks, activities, assessments, and metadata
    // - Provide search, filtering, and detail inspection
    //
    // Expected HTML hooks:
    //   <div id="course-engine-view"></div>
    //
    // Optional CSS classes:
    //   course-engine-shell
    //   course-engine-sidebar
    //   course-engine-main
    //   course-engine-toolbar
    //   course-engine-search
    //   course-engine-stats
    //   course-engine-list
    //   course-engine-card
    //   course-engine-card--active
    //   course-engine-detail
    //   course-engine-section
    //   course-engine-chip
    //   course-engine-empty
    //   course-engine-error
    // ============================================================
  
    const COURSE_ENGINE_INDEX_URL = "../../exports/course_engine/course_engine_index.json";
    const COURSE_ENGINE_PACKAGE_BASE = "../../exports/course_engine";
  
    const state = {
      index: null,
      packagesBySlug: new Map(),
      selectedCourseSlug: null,
      searchQuery: "",
      selectedLessonSlug: null,
      loadingIndex: false,
      loadingPackage: false,
      error: null,
    };
  
    // ------------------------------------------------------------
    // Utilities
    // ------------------------------------------------------------
  
    function el(tag, className = "", text = "") {
      const node = document.createElement(tag);
      if (className) node.className = className;
      if (text) node.textContent = text;
      return node;
    }
  
    function clear(node) {
      while (node.firstChild) {
        node.removeChild(node.firstChild);
      }
    }
  
    function safeArray(value) {
      return Array.isArray(value) ? value : [];
    }
  
    function number(value, fallback = 0) {
      return typeof value === "number" && Number.isFinite(value) ? value : fallback;
    }
  
    function humanize(value) {
      if (!value) return "";
      return String(value)
        .replace(/^course_\d+_/, "")
        .replace(/^chapter_\d+_/, "")
        .replace(/_/g, " ")
        .replace(/\s+/g, " ")
        .trim()
        .replace(/\b\w/g, (m) => m.toUpperCase());
    }
  
    function normalizeSearch(value) {
      return String(value || "").trim().toLowerCase();
    }
  
    function coursePackageUrl(slug) {
      return `${COURSE_ENGINE_PACKAGE_BASE}/${slug}/course_package.json`;
    }
  
    function buildCourseStats(pkg) {
      const lessons = safeArray(pkg?.lessons);
      const lessonCount = lessons.length;
      const blockCount = lessons.reduce((sum, lesson) => sum + safeArray(lesson.blocks).length, 0);
      const activityCount = lessons.reduce((sum, lesson) => sum + safeArray(lesson.activities).length, 0);
      const assessmentCount = lessons.reduce((sum, lesson) => sum + safeArray(lesson.assessments).length, 0);
      const objectiveCount = lessons.reduce((sum, lesson) => sum + safeArray(lesson.objectives).length, 0);
  
      return {
        lessonCount,
        blockCount,
        activityCount,
        assessmentCount,
        objectiveCount,
        totalEstimatedMinutes: number(pkg?.total_estimated_minutes, 0),
      };
    }
  
    function firstNonEmpty(...values) {
      for (const value of values) {
        if (value !== undefined && value !== null && String(value).trim() !== "") {
          return value;
        }
      }
      return "";
    }
  
    function truncate(text, max = 220) {
      const value = String(text || "").trim();
      if (value.length <= max) return value;
      return `${value.slice(0, max).trim()}…`;
    }
  
    // ------------------------------------------------------------
    // Data loading
    // ------------------------------------------------------------
  
    async function fetchJson(url) {
      const response = await fetch(url, { cache: "no-store" });
      if (!response.ok) {
        throw new Error(`Request failed (${response.status}) for ${url}`);
      }
      return response.json();
    }
  
    async function loadCourseEngineIndex() {
      state.loadingIndex = true;
      state.error = null;
      render();
  
      try {
        const index = await fetchJson(COURSE_ENGINE_INDEX_URL);
        state.index = index;
        const courses = safeArray(index?.courses);
  
        if (!state.selectedCourseSlug && courses.length > 0) {
          state.selectedCourseSlug = courses[0].slug;
        }
  
        state.loadingIndex = false;
        render();
  
        if (state.selectedCourseSlug) {
          await ensureCoursePackageLoaded(state.selectedCourseSlug);
        }
      } catch (error) {
        console.error(error);
        state.loadingIndex = false;
        state.error = `Failed to load course engine index. ${error.message}`;
        render();
      }
    }
  
    async function ensureCoursePackageLoaded(slug) {
      if (!slug) return;
      if (state.packagesBySlug.has(slug)) return;
  
      state.loadingPackage = true;
      state.error = null;
      render();
  
      try {
        const pkg = await fetchJson(coursePackageUrl(slug));
        state.packagesBySlug.set(slug, pkg);
  
        if (!state.selectedLessonSlug) {
          const firstLesson = safeArray(pkg?.lessons)[0];
          state.selectedLessonSlug = firstLesson?.slug || null;
        }
  
        state.loadingPackage = false;
        render();
      } catch (error) {
        console.error(error);
        state.loadingPackage = false;
        state.error = `Failed to load course package for ${slug}. ${error.message}`;
        render();
      }
    }
  
    // ------------------------------------------------------------
    // State helpers
    // ------------------------------------------------------------
  
    function getIndexedCourses() {
      return safeArray(state.index?.courses);
    }
  
    function getFilteredCourses() {
      const query = normalizeSearch(state.searchQuery);
      const courses = getIndexedCourses();
  
      if (!query) return courses;
  
      return courses.filter((course) => {
        const haystack = [
          course.slug,
          course.title,
          course.source_path,
        ]
          .map((value) => normalizeSearch(value))
          .join(" ");
  
        return haystack.includes(query);
      });
    }
  
    function getSelectedPackage() {
      if (!state.selectedCourseSlug) return null;
      return state.packagesBySlug.get(state.selectedCourseSlug) || null;
    }
  
    function getSelectedLesson(pkg) {
      const lessons = safeArray(pkg?.lessons);
      if (!lessons.length) return null;
  
      const found = lessons.find((lesson) => lesson.slug === state.selectedLessonSlug);
      return found || lessons[0];
    }
  
    function selectCourse(slug) {
      state.selectedCourseSlug = slug;
      state.selectedLessonSlug = null;
      render();
      ensureCoursePackageLoaded(slug);
    }
  
    function selectLesson(slug) {
      state.selectedLessonSlug = slug;
      render();
    }
  
    // ------------------------------------------------------------
    // Rendering
    // ------------------------------------------------------------
  
    function render() {
      const container = document.getElementById("course-engine-view");
      if (!container) return;
  
      clear(container);
  
      const shell = el("div", "course-engine-shell");
      const sidebar = el("aside", "course-engine-sidebar");
      const main = el("section", "course-engine-main");
  
      sidebar.appendChild(renderSidebar());
      main.appendChild(renderMain());
  
      shell.appendChild(sidebar);
      shell.appendChild(main);
      container.appendChild(shell);
    }
  
    function renderSidebar() {
      const wrapper = el("div", "course-engine-sidebar-inner");
  
      const header = el("div", "course-engine-toolbar");
      const title = el("h1", "course-engine-title", "Arkansas Civics Course Engine");
      const subtitle = el(
        "p",
        "course-engine-subtitle",
        "Browse internal course packages generated from the source content spine."
      );
  
      header.appendChild(title);
      header.appendChild(subtitle);
  
      const searchWrap = el("div", "course-engine-search-wrap");
      const search = document.createElement("input");
      search.type = "search";
      search.placeholder = "Search courses…";
      search.value = state.searchQuery;
      search.className = "course-engine-search";
      search.addEventListener("input", (event) => {
        state.searchQuery = event.target.value || "";
        render();
      });
      searchWrap.appendChild(search);
  
      wrapper.appendChild(header);
      wrapper.appendChild(searchWrap);
      wrapper.appendChild(renderGlobalStats());
      wrapper.appendChild(renderCourseList());
  
      return wrapper;
    }
  
    function renderGlobalStats() {
      const stats = el("div", "course-engine-stats");
  
      if (state.loadingIndex) {
        stats.appendChild(el("div", "course-engine-empty", "Loading course engine index…"));
        return stats;
      }
  
      const courses = getIndexedCourses();
      const filteredCourses = getFilteredCourses();
  
      stats.appendChild(statRow("Courses", String(courses.length)));
      stats.appendChild(statRow("Visible", String(filteredCourses.length)));
  
      if (state.index) {
        const generatedBy = firstNonEmpty(state.index.generated_by, "engine.course_engine");
        stats.appendChild(statRow("Generator", generatedBy));
      }
  
      return stats;
    }
  
    function renderCourseList() {
      const list = el("div", "course-engine-list");
  
      if (state.error) {
        list.appendChild(el("div", "course-engine-error", state.error));
      }
  
      const filteredCourses = getFilteredCourses();
  
      if (!filteredCourses.length) {
        list.appendChild(el("div", "course-engine-empty", "No courses match your search."));
        return list;
      }
  
      filteredCourses.forEach((course) => {
        const card = el("button", "course-engine-card");
        card.type = "button";
  
        if (course.slug === state.selectedCourseSlug) {
          card.classList.add("course-engine-card--active");
        }
  
        const title = el("div", "course-engine-card-title", firstNonEmpty(course.title, humanize(course.slug)));
        const meta = el(
          "div",
          "course-engine-card-meta",
          `${number(course.lesson_count)} lessons • ${number(course.total_estimated_minutes)} min`
        );
        const slug = el("div", "course-engine-card-slug", course.slug);
  
        card.appendChild(title);
        card.appendChild(meta);
        card.appendChild(slug);
  
        card.addEventListener("click", () => selectCourse(course.slug));
        list.appendChild(card);
      });
  
      return list;
    }
  
    function renderMain() {
      const wrapper = el("div", "course-engine-detail");
  
      if (state.loadingIndex) {
        wrapper.appendChild(el("div", "course-engine-empty", "Loading course engine index…"));
        return wrapper;
      }
  
      if (state.error && !getSelectedPackage()) {
        wrapper.appendChild(el("div", "course-engine-error", state.error));
        return wrapper;
      }
  
      if (!state.selectedCourseSlug) {
        wrapper.appendChild(el("div", "course-engine-empty", "Select a course to inspect its internal package."));
        return wrapper;
      }
  
      const pkg = getSelectedPackage();
  
      if (state.loadingPackage && !pkg) {
        wrapper.appendChild(el("div", "course-engine-empty", "Loading course package…"));
        return wrapper;
      }
  
      if (!pkg) {
        wrapper.appendChild(el("div", "course-engine-empty", "Course package not loaded yet."));
        return wrapper;
      }
  
      wrapper.appendChild(renderCourseHeader(pkg));
      wrapper.appendChild(renderLessonNavigator(pkg));
      wrapper.appendChild(renderLessonDetail(pkg));
  
      return wrapper;
    }
  
    function renderCourseHeader(pkg) {
      const header = el("div", "course-engine-section");
  
      const title = el("h2", "course-engine-detail-title", firstNonEmpty(pkg.title, humanize(pkg.slug)));
      const subtitle = el("div", "course-engine-detail-subtitle", pkg.slug);
  
      const stats = buildCourseStats(pkg);
      const statGrid = el("div", "course-engine-stat-grid");
      statGrid.appendChild(statRow("Lessons", String(stats.lessonCount)));
      statGrid.appendChild(statRow("Blocks", String(stats.blockCount)));
      statGrid.appendChild(statRow("Activities", String(stats.activityCount)));
      statGrid.appendChild(statRow("Assessments", String(stats.assessmentCount)));
      statGrid.appendChild(statRow("Objectives", String(stats.objectiveCount)));
      statGrid.appendChild(statRow("Estimated Time", `${stats.totalEstimatedMinutes} min`));
  
      const meta = el("div", "course-engine-meta");
      meta.appendChild(metaLine("Source", firstNonEmpty(pkg.source_path, "Unknown")));
      meta.appendChild(metaLine("Generated By", firstNonEmpty(pkg.metadata?.generated_by, "engine.course_engine")));
      meta.appendChild(metaLine("Source of Truth", firstNonEmpty(pkg.metadata?.source_of_truth, "content/courses")));
  
      header.appendChild(title);
      header.appendChild(subtitle);
      header.appendChild(statGrid);
      header.appendChild(meta);
  
      return header;
    }
  
    function renderLessonNavigator(pkg) {
      const section = el("div", "course-engine-section");
      section.appendChild(el("h3", "", "Lessons"));
  
      const lessons = safeArray(pkg.lessons);
      if (!lessons.length) {
        section.appendChild(el("div", "course-engine-empty", "This course package has no lessons."));
        return section;
      }
  
      const nav = el("div", "course-engine-lesson-nav");
  
      lessons.forEach((lesson, index) => {
        const button = el(
          "button",
          "course-engine-chip",
          `${index + 1}. ${firstNonEmpty(lesson.title, humanize(lesson.slug))}`
        );
        button.type = "button";
  
        const selectedLesson = getSelectedLesson(pkg);
        if (selectedLesson && selectedLesson.slug === lesson.slug) {
          button.classList.add("course-engine-chip--active");
        }
  
        button.addEventListener("click", () => selectLesson(lesson.slug));
        nav.appendChild(button);
      });
  
      section.appendChild(nav);
      return section;
    }
  
    function renderLessonDetail(pkg) {
      const section = el("div", "course-engine-section");
  
      const lesson = getSelectedLesson(pkg);
      if (!lesson) {
        section.appendChild(el("div", "course-engine-empty", "No lesson selected."));
        return section;
      }
  
      const title = el("h3", "", firstNonEmpty(lesson.title, humanize(lesson.slug)));
      const sub = el(
        "div",
        "course-engine-detail-subtitle",
        `${lesson.chapter_path || lesson.chapter_name || lesson.slug} • ${number(lesson.estimated_minutes)} min`
      );
  
      section.appendChild(title);
      section.appendChild(sub);
  
      section.appendChild(renderObjectives(lesson));
      section.appendChild(renderTags(lesson));
      section.appendChild(renderBlocks(lesson));
      section.appendChild(renderActivities(lesson));
      section.appendChild(renderAssessments(lesson));
      section.appendChild(renderLessonMetadata(lesson));
  
      return section;
    }
  
    function renderObjectives(lesson) {
      const section = el("div", "course-engine-subsection");
      section.appendChild(el("h4", "", "Objectives"));
  
      const objectives = safeArray(lesson.objectives);
      if (!objectives.length) {
        section.appendChild(el("div", "course-engine-empty", "No objectives generated."));
        return section;
      }
  
      const list = el("ul", "course-engine-bullets");
      objectives.forEach((objective) => {
        const item = el("li", "", `${objective.text} (${objective.bloom_level || "understand"})`);
        list.appendChild(item);
      });
  
      section.appendChild(list);
      return section;
    }
  
    function renderTags(lesson) {
      const section = el("div", "course-engine-subsection");
      section.appendChild(el("h4", "", "Tags"));
  
      const tags = safeArray(lesson.tags);
      if (!tags.length) {
        section.appendChild(el("div", "course-engine-empty", "No tags available."));
        return section;
      }
  
      const wrap = el("div", "course-engine-chip-wrap");
      tags.forEach((tag) => {
        wrap.appendChild(el("span", "course-engine-chip", tag));
      });
  
      section.appendChild(wrap);
      return section;
    }
  
    function renderBlocks(lesson) {
      const section = el("div", "course-engine-subsection");
      section.appendChild(el("h4", "", "Content Blocks"));
  
      const blocks = safeArray(lesson.blocks);
      if (!blocks.length) {
        section.appendChild(el("div", "course-engine-empty", "No content blocks generated."));
        return section;
      }
  
      const wrap = el("div", "course-engine-stack");
  
      blocks.forEach((block) => {
        const card = el("div", "course-engine-panel");
  
        const title = el(
          "div",
          "course-engine-panel-title",
          `${number(block.order)}. ${firstNonEmpty(block.title, humanize(block.source_segment_name))}`
        );
  
        const meta = el(
          "div",
          "course-engine-panel-meta",
          `Type: ${firstNonEmpty(block.block_type, "content")} • Source: ${firstNonEmpty(block.source_segment_name, "unknown")}`
        );
  
        const body = el("pre", "course-engine-panel-body");
        body.textContent = truncate(block.body, 1500);
  
        card.appendChild(title);
        card.appendChild(meta);
        card.appendChild(body);
        wrap.appendChild(card);
      });
  
      section.appendChild(wrap);
      return section;
    }
  
    function renderActivities(lesson) {
      const section = el("div", "course-engine-subsection");
      section.appendChild(el("h4", "", "Activities"));
  
      const activities = safeArray(lesson.activities);
      if (!activities.length) {
        section.appendChild(el("div", "course-engine-empty", "No activities generated."));
        return section;
      }
  
      const wrap = el("div", "course-engine-stack");
  
      activities.forEach((activity) => {
        const card = el("div", "course-engine-panel");
  
        card.appendChild(el("div", "course-engine-panel-title", firstNonEmpty(activity.title, "Untitled Activity")));
        card.appendChild(
          el(
            "div",
            "course-engine-panel-meta",
            `Type: ${firstNonEmpty(activity.activity_type, "activity")} • Minutes: ${number(activity.estimated_minutes)} • Source: ${firstNonEmpty(activity.source_segment_name, "unknown")}`
          )
        );
        card.appendChild(el("div", "course-engine-panel-text", firstNonEmpty(activity.instructions, "No instructions provided.")));
  
        wrap.appendChild(card);
      });
  
      section.appendChild(wrap);
      return section;
    }
  
    function renderAssessments(lesson) {
      const section = el("div", "course-engine-subsection");
      section.appendChild(el("h4", "", "Assessments"));
  
      const assessments = safeArray(lesson.assessments);
      if (!assessments.length) {
        section.appendChild(el("div", "course-engine-empty", "No assessments generated."));
        return section;
      }
  
      const wrap = el("div", "course-engine-stack");
  
      assessments.forEach((assessment) => {
        const card = el("div", "course-engine-panel");
  
        card.appendChild(
          el(
            "div",
            "course-engine-panel-title",
            `${firstNonEmpty(assessment.question_type, "question")} • ${number(assessment.points, 1)} point(s)`
          )
        );
        card.appendChild(el("div", "course-engine-panel-text", firstNonEmpty(assessment.prompt, "No prompt provided.")));
        card.appendChild(
          el(
            "div",
            "course-engine-panel-meta",
            `Guidance: ${firstNonEmpty(assessment.answer_guidance, "None")} • Source: ${firstNonEmpty(assessment.source_segment_name, "unknown")}`
          )
        );
  
        wrap.appendChild(card);
      });
  
      section.appendChild(wrap);
      return section;
    }
  
    function renderLessonMetadata(lesson) {
      const section = el("div", "course-engine-subsection");
      section.appendChild(el("h4", "", "Lesson Metadata"));
  
      const metaWrap = el("div", "course-engine-meta");
  
      metaWrap.appendChild(metaLine("Lesson Slug", firstNonEmpty(lesson.slug, "Unknown")));
      metaWrap.appendChild(metaLine("Chapter Name", firstNonEmpty(lesson.chapter_name, "Unknown")));
      metaWrap.appendChild(metaLine("Chapter Path", firstNonEmpty(lesson.chapter_path, "Unknown")));
      metaWrap.appendChild(metaLine("Estimated Minutes", String(number(lesson.estimated_minutes, 0))));
  
      if (lesson.metadata && typeof lesson.metadata === "object") {
        Object.entries(lesson.metadata).forEach(([key, value]) => {
          metaWrap.appendChild(metaLine(humanize(key), formatMetadataValue(value)));
        });
      }
  
      section.appendChild(metaWrap);
      return section;
    }
  
    function formatMetadataValue(value) {
      if (value === null || value === undefined) return "None";
      if (Array.isArray(value)) return value.join(", ");
      if (typeof value === "object") return JSON.stringify(value);
      return String(value);
    }
  
    function statRow(label, value) {
      const row = el("div", "course-engine-stat");
      row.appendChild(el("div", "course-engine-stat-label", label));
      row.appendChild(el("div", "course-engine-stat-value", value));
      return row;
    }
  
    function metaLine(label, value) {
      const row = el("div", "course-engine-meta-line");
      row.appendChild(el("strong", "", `${label}: `));
      row.appendChild(document.createTextNode(value));
      return row;
    }
  
    // ------------------------------------------------------------
    // Init
    // ------------------------------------------------------------
  
    window.ArkansasCivicsCourseEngineViewer = {
      reload: loadCourseEngineIndex,
      state,
    };
  
    window.addEventListener("load", loadCourseEngineIndex);
  })();