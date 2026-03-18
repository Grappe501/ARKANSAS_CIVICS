(() => {
  "use strict";

  const TRACK_INDEX_URL = "../../exports/tracks/track_index.json";
  const TRACK_BASE_URL = "../../exports/tracks";
  const RUNTIME_BLUEPRINT_URL = "../../exports/tracks/learning_runtime_blueprint.json";

  const state = {
    index: null,
    tracksBySlug: new Map(),
    selectedSlug: null,
    searchQuery: "",
    runtimeBlueprint: null,
    error: null,
  };

  function el(tag, className = "", text = "") {
    const node = document.createElement(tag);
    if (className) node.className = className;
    if (text) node.textContent = text;
    return node;
  }

  function clear(node) {
    while (node.firstChild) node.removeChild(node.firstChild);
  }

  function safeArray(value) {
    return Array.isArray(value) ? value : [];
  }

  async function fetchJson(url) {
    const response = await fetch(url, { cache: "no-store" });
    if (!response.ok) throw new Error(`Request failed (${response.status}) for ${url}`);
    return response.json();
  }

  async function loadIndex() {
    const root = document.getElementById("track-engine-view");
    if (!root) return;

    try {
      state.index = await fetchJson(TRACK_INDEX_URL);
      state.runtimeBlueprint = await fetchJson(RUNTIME_BLUEPRINT_URL).catch(() => null);
      const tracks = safeArray(state.index?.tracks);
      if (!state.selectedSlug && tracks.length) state.selectedSlug = tracks[0].slug;
      render();
      if (state.selectedSlug) await ensureTrackLoaded(state.selectedSlug);
    } catch (error) {
      console.error(error);
      state.error = `Failed to load track engine output. ${error.message}`;
      render();
    }
  }

  async function ensureTrackLoaded(slug) {
    if (!slug || state.tracksBySlug.has(slug)) return;
    try {
      const data = await fetchJson(`${TRACK_BASE_URL}/${slug}/track_definition.json`);
      state.tracksBySlug.set(slug, data);
      render();
    } catch (error) {
      console.error(error);
      state.error = `Failed to load track definition for ${slug}. ${error.message}`;
      render();
    }
  }

  function filteredTracks() {
    const tracks = safeArray(state.index?.tracks);
    const query = (state.searchQuery || "").trim().toLowerCase();
    if (!query) return tracks;
    return tracks.filter((track) => [track.slug, track.title, track.subtitle, track.audience]
      .join(" ")
      .toLowerCase()
      .includes(query));
  }

  function render() {
    const root = document.getElementById("track-engine-view");
    if (!root) return;
    clear(root);

    if (state.error) {
      root.appendChild(el("div", "course-engine-error", state.error));
    }

    const shell = el("div", "course-engine-shell");
    const sidebar = el("div", "course-engine-sidebar");
    const main = el("div", "course-engine-main");

    const heading = el("h3", "", "Track Engine");
    const sub = el("p", "panel-intro", "Role-based training pathways for Stand Up Arkansas.");
    const search = document.createElement("input");
    search.type = "search";
    search.placeholder = "Search tracks…";
    search.className = "course-engine-search";
    search.value = state.searchQuery;
    search.addEventListener("input", (event) => {
      state.searchQuery = event.target.value || "";
      render();
    });

    sidebar.appendChild(heading);
    sidebar.appendChild(sub);
    sidebar.appendChild(search);

    safeArray(filteredTracks()).forEach((track) => {
      const button = el("button", "course-engine-card");
      button.type = "button";
      if (track.slug === state.selectedSlug) button.classList.add("course-engine-card--active");
      button.appendChild(el("div", "course-engine-card-title", track.title));
      button.appendChild(el("div", "course-engine-card-meta", `${track.milestone_count} milestones • ${track.estimated_hours} hr`));
      button.appendChild(el("div", "course-engine-card-slug", track.slug));
      button.addEventListener("click", async () => {
        state.selectedSlug = track.slug;
        render();
        await ensureTrackLoaded(track.slug);
      });
      sidebar.appendChild(button);
    });

    const track = state.tracksBySlug.get(state.selectedSlug);
    if (!track) {
      main.appendChild(el("div", "course-engine-empty", "Select a track to inspect its pathway."));
    } else {
      main.appendChild(el("h2", "course-engine-detail-title", track.title));
      main.appendChild(el("div", "course-engine-detail-subtitle", track.subtitle || ""));
      main.appendChild(el("p", "", track.description || ""));

      const stats = el("div", "course-engine-stat-grid");
      [["Courses", track.course_count], ["Hours", track.estimated_hours], ["Milestones", safeArray(track.milestones).length], ["Audience", track.audience || "Public"]]
        .forEach(([label, value]) => {
          const stat = el("div", "course-engine-stat");
          stat.appendChild(el("div", "course-engine-stat-label", String(label)));
          stat.appendChild(el("div", "course-engine-stat-value", String(value)));
          stats.appendChild(stat);
        });
      main.appendChild(stats);

      if (safeArray(track.focus_tags).length) {
        const chipWrap = el("div", "course-engine-chip-wrap");
        safeArray(track.focus_tags).forEach((tag) => chipWrap.appendChild(el("span", "course-engine-chip", tag)));
        main.appendChild(chipWrap);
      }

      safeArray(track.milestones).forEach((milestone) => {
        const panel = el("div", "course-engine-panel");
        panel.appendChild(el("div", "course-engine-panel-title", `Level ${milestone.level}: ${milestone.title}`));
        panel.appendChild(el("div", "course-engine-panel-meta", `${milestone.badge} • ${milestone.target_hours} target hours`));
        panel.appendChild(el("div", "course-engine-panel-text", milestone.description || ""));
        const list = el("ul", "course-engine-bullets");
        safeArray(milestone.course_refs).forEach((ref) => {
          const item = el("li", "", `${ref.course_title} — ${ref.reason}`);
          list.appendChild(item);
        });
        panel.appendChild(list);
        main.appendChild(panel);
      });
    }

    if (state.runtimeBlueprint) {
      const runtimePanel = el("div", "course-engine-section");
      runtimePanel.appendChild(el("h3", "", "Learning Runtime Blueprint"));
      runtimePanel.appendChild(el("p", "", "The future active-learning clock, idle detection, and analytics runtime that will power education hours and volunteer reporting."));
      const chipWrap = el("div", "course-engine-chip-wrap");
      safeArray(state.runtimeBlueprint.reporting_targets).slice(0, 6).forEach((target) => chipWrap.appendChild(el("span", "course-engine-chip", target)));
      runtimePanel.appendChild(chipWrap);
      main.appendChild(runtimePanel);
    }

    shell.appendChild(sidebar);
    shell.appendChild(main);
    root.appendChild(shell);
  }

  window.StandUpArkansasTrackEngineViewer = { reload: loadIndex, state };
  window.addEventListener("load", loadIndex);
})();
