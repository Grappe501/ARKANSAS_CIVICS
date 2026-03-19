
(function () {
  const data = window.PHASE10_CONTENT || {};
  const courses = Array.isArray(data.courses) ? data.courses : [];
  const tracks = Array.isArray(data.tracks) ? data.tracks : [];

  const $ = (id) => document.getElementById(id);
  const els = {
    learnerLevel: $("learnerLevel"),
    completedCount: $("completedCount"),
    bookmarkCount: $("bookmarkCount"),
    estimatedHours: $("estimatedHours"),
    sessionMinutes: $("sessionMinutes"),
    completionBadge: $("completionBadge"),
    progressFill: $("progressFill"),
    resumeBtn: $("resumeBtn"),
    nextRecommendedBtn: $("nextRecommendedBtn"),
    nextRecommendation: $("nextRecommendation"),
    searchInput: $("searchInput"),
    courseSelect: $("courseSelect"),
    chapterSelect: $("chapterSelect"),
    segmentSelect: $("segmentSelect"),
    markCompleteBtn: $("markCompleteBtn"),
    bookmarkBtn: $("bookmarkBtn"),
    clearProgressBtn: $("clearProgressBtn"),
    searchCount: $("searchCount"),
    searchResults: $("searchResults"),
    bookmarkList: $("bookmarkList"),
    lessonTitle: $("lessonTitle"),
    lessonMeta: $("lessonMeta"),
    courseCount: $("courseCount"),
    chapterCount: $("chapterCount"),
    segmentCount: $("segmentCount"),
    streakCount: $("streakCount"),
    segmentHeading: $("segmentHeading"),
    activePath: $("activePath"),
    segmentTags: $("segmentTags"),
    wordCount: $("wordCount"),
    readTime: $("readTime"),
    whyItMatters: $("whyItMatters"),
    learningAction: $("learningAction"),
    segmentContent: $("segmentContent"),
    recommendedList: $("recommendedList"),
    segmentList: $("segmentList"),
    trackList: $("trackList"),
  };

  const STORAGE = {
    completed: "arkcivics_p10_completed",
    bookmarks: "arkcivics_p10_bookmarks",
    last: "arkcivics_p10_last",
    profile: "arkcivics_p10_profile",
    sessions: "arkcivics_p10_sessions",
  };

  const state = {
    selectedCourse: null,
    selectedChapter: null,
    selectedSegment: null,
    completed: loadJSON(STORAGE.completed, []),
    bookmarks: loadJSON(STORAGE.bookmarks, []),
    profile: loadJSON(STORAGE.profile, { startedAt: new Date().toISOString(), streak: 1 }),
    sessions: loadJSON(STORAGE.sessions, { totalMinutes: 0, lastOpenedAt: null }),
    searchIndex: [],
  };

  function loadJSON(key, fallback) {
    try {
      const value = JSON.parse(localStorage.getItem(key));
      return value == null ? fallback : value;
    } catch {
      return fallback;
    }
  }

  function saveJSON(key, value) {
    localStorage.setItem(key, JSON.stringify(value));
  }

  function segId(courseSlug, chapterSlug, segmentSlug) {
    return [courseSlug, chapterSlug, segmentSlug].join("::");
  }

  function currentCourse() {
    return courses.find(c => c.slug === state.selectedCourse) || courses[0] || null;
  }

  function currentChapter() {
    const course = currentCourse();
    return (course?.chapters || []).find(ch => ch.slug === state.selectedChapter) || (course?.chapters || [])[0] || null;
  }

  function currentSegment() {
    const chapter = currentChapter();
    return (chapter?.segments || []).find(seg => seg.slug === state.selectedSegment) || (chapter?.segments || [])[0] || null;
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

    for (const raw of lines) {
      const line = raw.trimEnd();
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

  function buildSearchIndex() {
    const rows = [];
    courses.forEach(course => {
      (course.chapters || []).forEach(chapter => {
        (chapter.segments || []).forEach(segment => {
          const id = segId(course.slug, chapter.slug, segment.slug);
          rows.push({
            id,
            courseSlug: course.slug,
            chapterSlug: chapter.slug,
            segmentSlug: segment.slug,
            courseTitle: course.title,
            chapterTitle: chapter.title,
            segmentTitle: segment.title,
            preview: segment.preview || "",
            wordCount: segment.word_count || 0,
            haystack: [
              course.title, chapter.title, segment.title, segment.content || "", (segment.tags || []).join(" ")
            ].join(" ").toLowerCase()
          });
        });
      });
    });
    state.searchIndex = rows;
  }

  function fillCourses() {
    els.courseSelect.innerHTML = "";
    courses.forEach(course => {
      const opt = document.createElement("option");
      opt.value = course.slug;
      opt.textContent = course.title;
      els.courseSelect.appendChild(opt);
    });
    if (!state.selectedCourse && courses[0]) state.selectedCourse = courses[0].slug;
    els.courseSelect.value = state.selectedCourse || "";
  }

  function fillChapters() {
    const course = currentCourse();
    els.chapterSelect.innerHTML = "";
    (course?.chapters || []).forEach(ch => {
      const opt = document.createElement("option");
      opt.value = ch.slug;
      opt.textContent = ch.title;
      els.chapterSelect.appendChild(opt);
    });
    if (!(course?.chapters || []).find(ch => ch.slug === state.selectedChapter)) {
      state.selectedChapter = (course?.chapters || [])[0]?.slug || null;
    }
    els.chapterSelect.value = state.selectedChapter || "";
  }

  function fillSegments() {
    const chapter = currentChapter();
    els.segmentSelect.innerHTML = "";
    (chapter?.segments || []).forEach(seg => {
      const opt = document.createElement("option");
      opt.value = seg.slug;
      opt.textContent = seg.title;
      els.segmentSelect.appendChild(opt);
    });
    if (!(chapter?.segments || []).find(seg => seg.slug === state.selectedSegment)) {
      state.selectedSegment = (chapter?.segments || [])[0]?.slug || null;
    }
    els.segmentSelect.value = state.selectedSegment || "";
  }

  function updateStats() {
    const totalSegments = data.segment_count || 0;
    const completed = state.completed.length;
    const pct = totalSegments ? Math.round((completed / totalSegments) * 100) : 0;
    const totalWords = state.completed.reduce((sum, id) => {
      const hit = state.searchIndex.find(x => x.id === id);
      return sum + (hit?.wordCount || 0);
    }, 0);
    const estimatedHours = Math.max(0, Math.round((totalWords / 200) / 60 * 10) / 10);
    const level = deriveLevel(completed);

    els.courseCount.textContent = data.course_count || courses.length || 0;
    els.chapterCount.textContent = data.chapter_count || 0;
    els.segmentCount.textContent = data.segment_count || 0;
    els.completedCount.textContent = completed;
    els.bookmarkCount.textContent = state.bookmarks.length;
    els.estimatedHours.textContent = `${estimatedHours}h`;
    els.sessionMinutes.textContent = `${state.sessions.totalMinutes || 0}m`;
    els.completionBadge.textContent = `${pct}%`;
    els.progressFill.style.width = `${pct}%`;
    els.learnerLevel.textContent = level.label;
    els.streakCount.textContent = `${state.profile.streak || 1} day`;
  }

  function deriveLevel(completed) {
    if (completed >= 250) return { label: "Level 5", name: "Movement Builder" };
    if (completed >= 120) return { label: "Level 4", name: "Organizer" };
    if (completed >= 50) return { label: "Level 3", name: "Community Voice" };
    if (completed >= 15) return { label: "Level 2", name: "Informed Citizen" };
    return { label: "Level 1", name: "Getting Started" };
  }

  function computeRecommendation() {
    const course = currentCourse();
    const chapter = currentChapter();
    const segment = currentSegment();
    if (!course || !chapter || !segment) return null;

    const segments = chapter.segments || [];
    const currentIndex = segments.findIndex(s => s.slug === segment.slug);
    for (let i = currentIndex + 1; i < segments.length; i++) {
      const next = segments[i];
      const id = segId(course.slug, chapter.slug, next.slug);
      if (!state.completed.includes(id)) {
        return {
          label: `${next.title} in ${chapter.title}`,
          courseSlug: course.slug,
          chapterSlug: chapter.slug,
          segmentSlug: next.slug,
          why: "Next uncompleted lesson in the current chapter."
        };
      }
    }

    for (const ch of course.chapters || []) {
      for (const seg of ch.segments || []) {
        const id = segId(course.slug, ch.slug, seg.slug);
        if (!state.completed.includes(id)) {
          return {
            label: `${seg.title} in ${ch.title}`,
            courseSlug: course.slug,
            chapterSlug: ch.slug,
            segmentSlug: seg.slug,
            why: "Next uncompleted lesson in the current course."
          };
        }
      }
    }
    return null;
  }

  function renderReader() {
    const course = currentCourse();
    const chapter = currentChapter();
    const segment = currentSegment();

    if (!course || !chapter || !segment) {
      els.lessonTitle.textContent = "No course data found";
      els.lessonMeta.textContent = "Run the Phase 10 build script to generate the real content bundle.";
      els.segmentHeading.textContent = "Content unavailable";
      els.segmentContent.innerHTML = "<p>No real course content is available yet.</p>";
      return;
    }

    const currentId = segId(course.slug, chapter.slug, segment.slug);

    els.lessonTitle.textContent = course.title;
    els.lessonMeta.textContent = chapter.title;
    els.segmentHeading.textContent = segment.title;
    els.activePath.textContent = `${course.title} → ${chapter.title} → ${segment.title}`;
    els.wordCount.textContent = `${segment.word_count || 0} words`;
    els.readTime.textContent = `${Math.max(1, Math.ceil((segment.word_count || 0) / 200))} min read`;
    els.segmentTags.innerHTML = (segment.tags || []).map(tag => `<span class="tag">${tag}</span>`).join("");
    els.segmentContent.innerHTML = renderMarkdown(segment.content || "");

    const purpose = chapter.title.includes("Pulling Up More Chairs")
      ? "This lesson helps readers move from observation into local civic participation."
      : "This lesson strengthens the civic context and practical understanding needed for effective action.";
    els.whyItMatters.textContent = purpose;
    els.learningAction.textContent = state.completed.includes(currentId)
      ? "This lesson is already completed. Use the recommended next lesson or bookmark this page for reference."
      : "Read this lesson, mark it complete, then continue to the next recommended segment.";

    saveJSON(STORAGE.last, {
      courseSlug: course.slug,
      chapterSlug: chapter.slug,
      segmentSlug: segment.slug
    });

    els.markCompleteBtn.disabled = state.completed.includes(currentId);
    els.markCompleteBtn.textContent = state.completed.includes(currentId) ? "Completed" : "Mark complete";
  }

  function renderSearchResults(query) {
    const q = String(query || "").trim().toLowerCase();
    if (!q) {
      els.searchCount.textContent = "0";
      els.searchResults.className = "results empty";
      els.searchResults.textContent = "Start typing to search the course library.";
      return;
    }

    const scored = state.searchIndex.map(row => {
      let score = 0;
      const title = row.segmentTitle.toLowerCase();
      const chapter = row.chapterTitle.toLowerCase();
      const course = row.courseTitle.toLowerCase();
      if (title.includes(q)) score += 8;
      if (chapter.includes(q)) score += 5;
      if (course.includes(q)) score += 4;
      if (row.haystack.includes(q)) score += 2;
      return { ...row, score };
    }).filter(x => x.score > 0).sort((a, b) => b.score - a.score).slice(0, 40);

    els.searchCount.textContent = String(scored.length);
    els.searchResults.innerHTML = "";
    els.searchResults.className = "results";

    if (!scored.length) {
      els.searchResults.className = "results empty";
      els.searchResults.textContent = "No matches found.";
      return;
    }

    scored.forEach(row => {
      const btn = document.createElement("button");
      btn.className = "result-item";
      btn.innerHTML = `<strong>${row.segmentTitle}</strong><small>${row.courseTitle} → ${row.chapterTitle}</small>`;
      btn.addEventListener("click", () => {
        state.selectedCourse = row.courseSlug;
        state.selectedChapter = row.chapterSlug;
        state.selectedSegment = row.segmentSlug;
        sync();
      });
      els.searchResults.appendChild(btn);
    });
  }

  function renderBookmarks() {
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

  function renderRecommendations() {
    const rec = computeRecommendation();
    els.recommendedList.innerHTML = "";
    if (!rec) {
      els.nextRecommendation.textContent = "You have completed everything in this current path.";
      els.recommendedList.innerHTML = '<div class="muted">No further recommendation in this course right now.</div>';
      return;
    }

    els.nextRecommendation.textContent = `${rec.label} — ${rec.why}`;
    const btn = document.createElement("button");
    btn.className = "rail-item";
    btn.innerHTML = `<strong>${rec.label}</strong><small>${rec.why}</small>`;
    btn.addEventListener("click", () => {
      state.selectedCourse = rec.courseSlug;
      state.selectedChapter = rec.chapterSlug;
      state.selectedSegment = rec.segmentSlug;
      sync();
    });
    els.recommendedList.appendChild(btn);
  }

  function renderNavigator() {
    const course = currentCourse();
    const chapter = currentChapter();
    const segments = chapter?.segments || [];
    const active = segId(course?.slug, chapter?.slug, state.selectedSegment);

    els.segmentList.innerHTML = "";
    segments.forEach(seg => {
      const btn = document.createElement("button");
      const id = segId(course.slug, chapter.slug, seg.slug);
      btn.className = "rail-item" + (id === active ? " active" : "");
      btn.innerHTML = `<strong>${seg.title}</strong><small>${seg.word_count || 0} words</small>`;
      btn.addEventListener("click", () => {
        state.selectedSegment = seg.slug;
        sync();
      });
      els.segmentList.appendChild(btn);
    });
  }

  function renderTracks() {
    els.trackList.innerHTML = "";
    const builtTracks = tracks.length ? tracks : [
      { title: "New Citizen Path", copy: "Start with the current course and complete segments in order." },
      { title: "Organizer Path", copy: "Focus on participation, strategy, systems, and action-oriented lessons." },
      { title: "Deep Study Path", copy: "Use bookmarks to collect research-heavy segments for later review." },
    ];

    builtTracks.forEach(track => {
      const card = document.createElement("div");
      card.className = "rail-item";
      card.innerHTML = `<strong>${track.title}</strong><small>${track.copy}</small>`;
      els.trackList.appendChild(card);
    });
  }

  function addBookmark() {
    const course = currentCourse();
    const chapter = currentChapter();
    const segment = currentSegment();
    if (!course || !chapter || !segment) return;
    const id = segId(course.slug, chapter.slug, segment.slug);
    if (state.bookmarks.some(x => x.id === id)) return;

    state.bookmarks.unshift({
      id,
      courseSlug: course.slug,
      chapterSlug: chapter.slug,
      segmentSlug: segment.slug,
      courseTitle: course.title,
      chapterTitle: chapter.title,
      segmentTitle: segment.title
    });
    saveJSON(STORAGE.bookmarks, state.bookmarks);
    renderBookmarks();
    updateStats();
  }

  function markComplete() {
    const course = currentCourse();
    const chapter = currentChapter();
    const segment = currentSegment();
    if (!course || !chapter || !segment) return;
    const id = segId(course.slug, chapter.slug, segment.slug);
    if (!state.completed.includes(id)) {
      state.completed.push(id);
      saveJSON(STORAGE.completed, state.completed);
    }
    updateStats();
    renderReader();
    renderRecommendations();
  }

  function resetAll() {
    localStorage.removeItem(STORAGE.completed);
    localStorage.removeItem(STORAGE.bookmarks);
    localStorage.removeItem(STORAGE.last);
    localStorage.removeItem(STORAGE.sessions);
    state.completed = [];
    state.bookmarks = [];
    state.sessions = { totalMinutes: 0, lastOpenedAt: null };
    sync();
  }

  function resumeLast() {
    const last = loadJSON(STORAGE.last, null);
    if (!last) return;
    state.selectedCourse = last.courseSlug;
    state.selectedChapter = last.chapterSlug;
    state.selectedSegment = last.segmentSlug;
    sync();
  }

  function goRecommended() {
    const rec = computeRecommendation();
    if (!rec) return;
    state.selectedCourse = rec.courseSlug;
    state.selectedChapter = rec.chapterSlug;
    state.selectedSegment = rec.segmentSlug;
    sync();
  }

  function updateSessionTime() {
    state.sessions.totalMinutes = Math.max(0, Number(state.sessions.totalMinutes || 0));
    const lastOpened = state.sessions.lastOpenedAt ? new Date(state.sessions.lastOpenedAt) : null;
    const now = new Date();

    if (!lastOpened || now.toDateString() !== lastOpened.toDateString()) {
      state.profile.streak = Math.max(1, Number(state.profile.streak || 1));
      saveJSON(STORAGE.profile, state.profile);
    }

    state.sessions.totalMinutes += 1;
    state.sessions.lastOpenedAt = now.toISOString();
    saveJSON(STORAGE.sessions, state.sessions);
    updateStats();
  }

  function sync() {
    fillCourses();
    fillChapters();
    fillSegments();
    renderReader();
    renderBookmarks();
    renderRecommendations();
    renderNavigator();
    renderTracks();
    updateStats();
    renderSearchResults(els.searchInput.value);
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
    els.searchInput.addEventListener("input", (e) => renderSearchResults(e.target.value));
    els.markCompleteBtn.addEventListener("click", markComplete);
    els.bookmarkBtn.addEventListener("click", addBookmark);
    els.clearProgressBtn.addEventListener("click", resetAll);
    els.resumeBtn.addEventListener("click", resumeLast);
    els.nextRecommendedBtn.addEventListener("click", goRecommended);
  }

  function boot() {
    if (!courses.length) {
      els.lessonTitle.textContent = "No course data found";
      els.lessonMeta.textContent = "Run the Phase 10 build script to generate the real content bundle.";
      return;
    }
    buildSearchIndex();
    const last = loadJSON(STORAGE.last, null);
    state.selectedCourse = last?.courseSlug || courses[0].slug;
    state.selectedChapter = last?.chapterSlug || null;
    state.selectedSegment = last?.segmentSlug || null;
    bindEvents();
    sync();
    setInterval(updateSessionTime, 60000);
  }

  boot();
})();
