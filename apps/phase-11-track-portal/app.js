
(function () {
  const data = window.PHASE11_CONTENT || {};
  const courses = Array.isArray(data.courses) ? data.courses : [];
  const roles = Array.isArray(data.roles) ? data.roles : [];

  const $ = (id) => document.getElementById(id);
  const els = {
    roleModal: $("roleModal"),
    roleOptions: $("roleOptions"),
    closeRoleModalBtn: $("closeRoleModalBtn"),
    learnerLevel: $("learnerLevel"),
    activeRoleLabel: $("activeRoleLabel"),
    activeTrackSummary: $("activeTrackSummary"),
    completedCount: $("completedCount"),
    bookmarkCount: $("bookmarkCount"),
    unlockedCount: $("unlockedCount"),
    sessionMinutes: $("sessionMinutes"),
    levelProgressLabel: $("levelProgressLabel"),
    levelProgressFill: $("levelProgressFill"),
    completionBadge: $("completionBadge"),
    progressFill: $("progressFill"),
    gateList: $("gateList"),
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
    lessonTitle: $("lessonTitle"),
    lessonMeta: $("lessonMeta"),
    courseCount: $("courseCount"),
    chapterCount: $("chapterCount"),
    segmentCount: $("segmentCount"),
    activeTrackHero: $("activeTrackHero"),
    segmentHeading: $("segmentHeading"),
    activePath: $("activePath"),
    segmentTags: $("segmentTags"),
    wordCount: $("wordCount"),
    readTime: $("readTime"),
    unlockStatus: $("unlockStatus"),
    whyItMatters: $("whyItMatters"),
    learningAction: $("learningAction"),
    segmentContent: $("segmentContent"),
    recommendedList: $("recommendedList"),
    trackQueue: $("trackQueue"),
    segmentList: $("segmentList"),
    bookmarkList: $("bookmarkList"),
    changeRoleBtn: $("changeRoleBtn"),
  };

  const STORAGE = {
    completed: "arkcivics_p11_completed",
    bookmarks: "arkcivics_p11_bookmarks",
    last: "arkcivics_p11_last",
    profile: "arkcivics_p11_profile",
    sessions: "arkcivics_p11_sessions",
  };

  const LEVELS = [
    { label: "Level 1", name: "Getting Started", min: 0, max: 14 },
    { label: "Level 2", name: "Informed Citizen", min: 15, max: 49 },
    { label: "Level 3", name: "Community Voice", min: 50, max: 119 },
    { label: "Level 4", name: "Organizer", min: 120, max: 249 },
    { label: "Level 5", name: "Power Builder", min: 250, max: Infinity },
  ];

  const state = {
    selectedCourse: null,
    selectedChapter: null,
    selectedSegment: null,
    completed: loadJSON(STORAGE.completed, []),
    bookmarks: loadJSON(STORAGE.bookmarks, []),
    profile: loadJSON(STORAGE.profile, { startedAt: new Date().toISOString(), activeRoleId: null }),
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

  function currentRole() {
    return roles.find(r => r.id === state.profile.activeRoleId) || null;
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

  function rolePriorityScore(role, row) {
    if (!role) return 0;
    let score = 0;
    if ((role.priority_courses || []).includes(row.courseSlug)) score += 10;
    const haystack = [row.courseTitle, row.chapterTitle, row.segmentTitle, ...(row.tags || [])].join(" ").toLowerCase();
    (role.priority_tags || []).forEach(tag => { if (haystack.includes(tag.toLowerCase())) score += 6; });
    return score;
  }

  function isUnlocked(row) {
    const role = currentRole();
    if (!role) return true;
    const gates = Array.isArray(role.gates) ? role.gates : [];
    const gate = gates.find(g => g.target_course === row.courseSlug);
    if (!gate) return true;
    const completed = state.completed.length;
    const roleChosen = !!state.profile.activeRoleId;
    if (gate.requires_role && !roleChosen) return false;
    if ((gate.min_completed || 0) > completed) return false;
    return true;
  }

  function currentLevel() {
    const completed = state.completed.length;
    return LEVELS.find(l => completed >= l.min && completed <= l.max) || LEVELS[0];
  }

  function nextLevel() {
    const completed = state.completed.length;
    return LEVELS.find(l => l.min > completed) || null;
  }

  function buildSearchIndex() {
    const rows = [];
    courses.forEach(course => {
      (course.chapters || []).forEach(chapter => {
        (chapter.segments || []).forEach(segment => {
          rows.push({
            id: segId(course.slug, chapter.slug, segment.slug),
            courseSlug: course.slug,
            chapterSlug: chapter.slug,
            segmentSlug: segment.slug,
            courseTitle: course.title,
            chapterTitle: chapter.title,
            segmentTitle: segment.title,
            tags: segment.tags || [],
            wordCount: segment.word_count || 0,
            preview: segment.preview || "",
            content: segment.content || "",
            haystack: [course.title, chapter.title, segment.title, segment.content || "", (segment.tags || []).join(" ")].join(" ").toLowerCase()
          });
        });
      });
    });
    state.searchIndex = rows;
  }

  function renderMarkdown(md) {
    const escape = (s) => String(s).replaceAll("&", "&amp;").replaceAll("<", "&lt;").replaceAll(">", "&gt;");
    const lines = String(md || "").replace(/\r\n/g, "\n").split("\n");
    let html = "", inList = false;
    const closeList = () => { if (inList) { html += "</ul>"; inList = false; } };
    for (const raw of lines) {
      const line = raw.trimEnd();
      if (!line.trim()) { closeList(); continue; }
      if (line.startsWith("### ")) { closeList(); html += `<h3>${escape(line.slice(4))}</h3>`; }
      else if (line.startsWith("## ")) { closeList(); html += `<h2>${escape(line.slice(3))}</h2>`; }
      else if (line.startsWith("# ")) { closeList(); html += `<h1>${escape(line.slice(2))}</h1>`; }
      else if (line.startsWith("- ")) { if (!inList) { html += "<ul>"; inList = true; } html += `<li>${escape(line.slice(2))}</li>`; }
      else if (/^---+$/.test(line.trim())) { closeList(); html += "<hr />"; }
      else { closeList(); html += `<p>${escape(line)}</p>`; }
    }
    closeList();
    return html || "<p>No content available for this segment yet.</p>";
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
      const role = currentRole();
      state.selectedCourse = role?.priority_courses?.[0] || courses[0].slug;
    }
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
      const row = state.searchIndex.find(r => r.id === segId(currentCourse().slug, chapter.slug, seg.slug));
      const locked = row ? !isUnlocked(row) : false;
      const opt = document.createElement("option");
      opt.value = seg.slug;
      opt.textContent = locked ? `${seg.title} 🔒` : seg.title;
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
    const unlocked = state.searchIndex.filter(isUnlocked).length;
    const level = currentLevel();
    const next = nextLevel();
    const levelSpan = next ? (next.min - level.min) : 1;
    const levelProgress = next ? Math.max(0, Math.min(100, Math.round(((completed - level.min) / levelSpan) * 100))) : 100;

    els.courseCount.textContent = data.course_count || courses.length || 0;
    els.chapterCount.textContent = data.chapter_count || 0;
    els.segmentCount.textContent = data.segment_count || 0;
    els.completedCount.textContent = completed;
    els.bookmarkCount.textContent = state.bookmarks.length;
    els.unlockedCount.textContent = unlocked;
    els.sessionMinutes.textContent = `${state.sessions.totalMinutes || 0}m`;
    els.completionBadge.textContent = `${pct}%`;
    els.progressFill.style.width = `${pct}%`;
    els.learnerLevel.textContent = `${level.label}`;
    els.levelProgressLabel.textContent = `${levelProgress}%`;
    els.levelProgressFill.style.width = `${levelProgress}%`;

    const role = currentRole();
    els.activeRoleLabel.textContent = role ? role.title : "Not chosen";
    els.activeTrackHero.textContent = role ? role.title : "No role";
    els.activeTrackSummary.textContent = role ? role.description : "Choose a role to activate a guided path through the platform.";
  }

  function renderRoleOptions() {
    els.roleOptions.innerHTML = "";
    roles.forEach(role => {
      const btn = document.createElement("button");
      btn.className = "role-item";
      btn.innerHTML = `<strong>${role.title}</strong><small>${role.description}</small>`;
      btn.addEventListener("click", () => {
        state.profile.activeRoleId = role.id;
        saveJSON(STORAGE.profile, state.profile);
        els.roleModal.classList.add("hidden");
        const preferred = role.priority_courses?.[0];
        if (preferred) state.selectedCourse = preferred;
        state.selectedChapter = null;
        state.selectedSegment = null;
        sync();
      });
      els.roleOptions.appendChild(btn);
    });
  }

  function maybeShowRoleModal() {
    if (!state.profile.activeRoleId) els.roleModal.classList.remove("hidden");
  }

  function renderGateList() {
    const role = currentRole();
    if (!role) {
      els.gateList.className = "results empty";
      els.gateList.textContent = "Choose a role to see progression gates.";
      return;
    }
    const gates = role.gates || [];
    els.gateList.className = "results";
    els.gateList.innerHTML = "";
    gates.forEach(g => {
      const unlocked = state.completed.length >= (g.min_completed || 0);
      const div = document.createElement("div");
      div.className = "gate-item" + (unlocked ? "" : " locked");
      div.innerHTML = `<strong>${g.title}</strong><small>${g.description}</small><small>${unlocked ? "Unlocked" : `Requires ${g.min_completed} completed lessons`}</small>`;
      els.gateList.appendChild(div);
    });
  }

  function renderReader() {
    const course = currentCourse();
    const chapter = currentChapter();
    const segment = currentSegment();
    if (!course || !chapter || !segment) {
      els.lessonTitle.textContent = "No course data found";
      els.lessonMeta.textContent = "Run the Phase 11 build script to generate the real content bundle.";
      els.segmentHeading.textContent = "Content unavailable";
      els.segmentContent.innerHTML = "<p>No real course content is available yet.</p>";
      return;
    }

    const row = state.searchIndex.find(r => r.id === segId(course.slug, chapter.slug, segment.slug));
    const unlocked = row ? isUnlocked(row) : true;

    els.lessonTitle.textContent = course.title;
    els.lessonMeta.textContent = chapter.title;
    els.segmentHeading.textContent = segment.title;
    els.activePath.textContent = `${course.title} → ${chapter.title} → ${segment.title}`;
    els.wordCount.textContent = `${segment.word_count || 0} words`;
    els.readTime.textContent = `${Math.max(1, Math.ceil((segment.word_count || 0) / 200))} min read`;
    els.segmentTags.innerHTML = (segment.tags || []).map(tag => `<span class="tag">${tag}</span>`).join("");
    els.unlockStatus.textContent = unlocked ? "Unlocked" : "Locked by gate";
    els.unlockStatus.className = unlocked ? "pill good" : "pill warning";

    const role = currentRole();
    if (!unlocked) {
      els.segmentContent.innerHTML = "<p>This lesson is currently locked for your active role. Complete earlier lessons to unlock it.</p>";
      els.learningAction.textContent = "Follow the recommended next lesson to unlock this content.";
    } else {
      els.segmentContent.innerHTML = renderMarkdown(segment.content || "");
      els.learningAction.textContent = role
        ? `As a ${role.title}, complete this lesson and continue through the guided queue.`
        : "Choose a role to activate guided progression and unlock-aware recommendations.";
    }

    els.whyItMatters.textContent = role
      ? `${role.title} path: this lesson supports your role by building context, language, and practical civic fluency.`
      : "This lesson builds civic fluency and practical movement knowledge.";

    saveJSON(STORAGE.last, { courseSlug: course.slug, chapterSlug: chapter.slug, segmentSlug: segment.slug });

    const currentId = segId(course.slug, chapter.slug, segment.slug);
    els.markCompleteBtn.disabled = !unlocked || state.completed.includes(currentId);
    els.markCompleteBtn.textContent = state.completed.includes(currentId) ? "Completed" : (unlocked ? "Mark complete" : "Locked");
  }

  function renderSearchResults(query) {
    const q = String(query || "").trim().toLowerCase();
    if (!q) {
      els.searchCount.textContent = "0";
      els.searchResults.className = "results empty";
      els.searchResults.textContent = "Start typing to search the course library.";
      return;
    }

    const role = currentRole();
    const scored = state.searchIndex.map(row => {
      let score = 0;
      if (row.segmentTitle.toLowerCase().includes(q)) score += 8;
      if (row.chapterTitle.toLowerCase().includes(q)) score += 5;
      if (row.courseTitle.toLowerCase().includes(q)) score += 4;
      if (row.haystack.includes(q)) score += 2;
      score += rolePriorityScore(role, row);
      if (isUnlocked(row)) score += 1;
      return { ...row, score, unlocked: isUnlocked(row) };
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
      btn.className = "result-item" + (row.unlocked ? "" : " locked");
      btn.innerHTML = `<strong>${row.segmentTitle}${row.unlocked ? "" : " 🔒"}</strong><small>${row.courseTitle} → ${row.chapterTitle}</small>`;
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
    els.bookmarkList.className = "rail-list";
    state.bookmarks.forEach(item => {
      const btn = document.createElement("button");
      btn.className = "rail-item";
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

  function computeRecommendation() {
    const role = currentRole();
    const rows = [...state.searchIndex]
      .filter(row => !state.completed.includes(row.id) && isUnlocked(row))
      .sort((a, b) => rolePriorityScore(role, b) - rolePriorityScore(role, a));

    if (role) {
      const roleRow = rows.find(r => (role.priority_courses || []).includes(r.courseSlug));
      if (roleRow) return roleRow;
    }
    return rows[0] || null;
  }

  function renderRecommendations() {
    const rec = computeRecommendation();
    els.recommendedList.innerHTML = "";
    els.trackQueue.innerHTML = "";

    if (!rec) {
      els.nextRecommendation.textContent = "No unlocked recommendation is available right now.";
      els.recommendedList.innerHTML = '<div class="muted">Complete more lessons or change role.</div>';
      return;
    }

    els.nextRecommendation.textContent = `${rec.segmentTitle} in ${rec.chapterTitle}`;
    const main = document.createElement("button");
    main.className = "rail-item";
    main.innerHTML = `<strong>${rec.segmentTitle}</strong><small>${rec.courseTitle} → ${rec.chapterTitle}</small>`;
    main.addEventListener("click", () => {
      state.selectedCourse = rec.courseSlug;
      state.selectedChapter = rec.chapterSlug;
      state.selectedSegment = rec.segmentSlug;
      sync();
    });
    els.recommendedList.appendChild(main);

    const role = currentRole();
    const queue = state.searchIndex
      .filter(row => !state.completed.includes(row.id) && isUnlocked(row))
      .sort((a, b) => (rolePriorityScore(role, b) - rolePriorityScore(role, a)) || (a.courseSlug.localeCompare(b.courseSlug)))
      .slice(0, 8);

    queue.forEach(row => {
      const btn = document.createElement("button");
      btn.className = "rail-item";
      btn.innerHTML = `<strong>${row.segmentTitle}</strong><small>${row.courseTitle}</small>`;
      btn.addEventListener("click", () => {
        state.selectedCourse = row.courseSlug;
        state.selectedChapter = row.chapterSlug;
        state.selectedSegment = row.segmentSlug;
        sync();
      });
      els.trackQueue.appendChild(btn);
    });
  }

  function renderNavigator() {
    const course = currentCourse();
    const chapter = currentChapter();
    const segments = chapter?.segments || [];
    const active = segId(course?.slug, chapter?.slug, state.selectedSegment);
    els.segmentList.innerHTML = "";
    segments.forEach(seg => {
      const id = segId(course.slug, chapter.slug, seg.slug);
      const row = state.searchIndex.find(r => r.id === id);
      const unlocked = row ? isUnlocked(row) : true;
      const btn = document.createElement("button");
      btn.className = "rail-item" + (id === active ? " active" : "") + (unlocked ? "" : " locked");
      btn.innerHTML = `<strong>${seg.title}${unlocked ? "" : " 🔒"}</strong><small>${seg.word_count || 0} words</small>`;
      btn.addEventListener("click", () => {
        state.selectedSegment = seg.slug;
        sync();
      });
      els.segmentList.appendChild(btn);
    });
  }

  function addBookmark() {
    const course = currentCourse(), chapter = currentChapter(), segment = currentSegment();
    if (!course || !chapter || !segment) return;
    const id = segId(course.slug, chapter.slug, segment.slug);
    if (state.bookmarks.some(x => x.id === id)) return;
    state.bookmarks.unshift({
      id, courseSlug: course.slug, chapterSlug: chapter.slug, segmentSlug: segment.slug,
      courseTitle: course.title, chapterTitle: chapter.title, segmentTitle: segment.title
    });
    saveJSON(STORAGE.bookmarks, state.bookmarks);
    renderBookmarks();
    updateStats();
  }

  function markComplete() {
    const course = currentCourse(), chapter = currentChapter(), segment = currentSegment();
    if (!course || !chapter || !segment) return;
    const id = segId(course.slug, chapter.slug, segment.slug);
    const row = state.searchIndex.find(r => r.id === id);
    if (row && !isUnlocked(row)) return;
    if (!state.completed.includes(id)) {
      state.completed.push(id);
      saveJSON(STORAGE.completed, state.completed);
    }
    updateStats();
    renderReader();
    renderGateList();
    renderRecommendations();
    renderNavigator();
  }

  function resetAll() {
    localStorage.removeItem(STORAGE.completed);
    localStorage.removeItem(STORAGE.bookmarks);
    localStorage.removeItem(STORAGE.last);
    localStorage.removeItem(STORAGE.sessions);
    localStorage.removeItem(STORAGE.profile);
    state.completed = [];
    state.bookmarks = [];
    state.profile = { startedAt: new Date().toISOString(), activeRoleId: null };
    state.sessions = { totalMinutes: 0, lastOpenedAt: null };
    maybeShowRoleModal();
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
    state.sessions.totalMinutes = Math.max(0, Number(state.sessions.totalMinutes || 0)) + 1;
    state.sessions.lastOpenedAt = new Date().toISOString();
    saveJSON(STORAGE.sessions, state.sessions);
    updateStats();
  }

  function sync() {
    fillCourses();
    fillChapters();
    fillSegments();
    updateStats();
    renderGateList();
    renderReader();
    renderRecommendations();
    renderNavigator();
    renderBookmarks();
    renderSearchResults(els.searchInput.value);
  }

  function bindEvents() {
    els.courseSelect.addEventListener("change", () => { state.selectedCourse = els.courseSelect.value; state.selectedChapter = null; state.selectedSegment = null; sync(); });
    els.chapterSelect.addEventListener("change", () => { state.selectedChapter = els.chapterSelect.value; state.selectedSegment = null; sync(); });
    els.segmentSelect.addEventListener("change", () => { state.selectedSegment = els.segmentSelect.value; sync(); });
    els.searchInput.addEventListener("input", (e) => renderSearchResults(e.target.value));
    els.markCompleteBtn.addEventListener("click", markComplete);
    els.bookmarkBtn.addEventListener("click", addBookmark);
    els.clearProgressBtn.addEventListener("click", resetAll);
    els.resumeBtn.addEventListener("click", resumeLast);
    els.nextRecommendedBtn.addEventListener("click", goRecommended);
    els.changeRoleBtn.addEventListener("click", () => els.roleModal.classList.remove("hidden"));
    els.closeRoleModalBtn.addEventListener("click", () => els.roleModal.classList.add("hidden"));
  }

  function boot() {
    if (!courses.length) {
      els.lessonTitle.textContent = "No course data found";
      els.lessonMeta.textContent = "Run the Phase 11 build script to generate the real content bundle.";
      return;
    }
    buildSearchIndex();
    renderRoleOptions();
    const last = loadJSON(STORAGE.last, null);
    state.selectedCourse = last?.courseSlug || currentRole()?.priority_courses?.[0] || courses[0].slug;
    state.selectedChapter = last?.chapterSlug || null;
    state.selectedSegment = last?.segmentSlug || null;
    bindEvents();
    sync();
    maybeShowRoleModal();
    setInterval(updateSessionTime, 60000);
  }

  boot();
})();
