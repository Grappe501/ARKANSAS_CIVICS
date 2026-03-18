(() => {
  "use strict";

  const DASHBOARD_URL = "../../exports/civic_intelligence/civic_intelligence_dashboard.json";

  function $(id) {
    return document.getElementById(id);
  }

  function clear(node) {
    while (node.firstChild) node.removeChild(node.firstChild);
  }

  function el(tag, className = "", text = "") {
    const node = document.createElement(tag);
    if (className) node.className = className;
    if (text) node.textContent = text;
    return node;
  }

  async function fetchDashboard() {
    const response = await fetch(DASHBOARD_URL, { cache: "no-store" });
    if (!response.ok) {
      throw new Error(`Failed to load dashboard (${response.status})`);
    }
    return response.json();
  }

  function renderStatGrid(payload) {
    const root = $("cidStatGrid");
    clear(root);

    const health = payload.system_health || {};
    const analytics = payload.analytics_summary || {};

    const stats = [
      ["Courses", payload.map_summary?.course_count || 0],
      ["Tracks", payload.track_summary?.track_count || 0],
      ["Learners", analytics.learner_count || 0],
      ["Active Hours", analytics.total_active_hours || 0],
      ["Badges", health.badge_count || 0],
      ["Graph Nodes", payload.graph_summary?.node_count || 0],
    ];

    stats.forEach(([label, value]) => {
      const card = el("div", "cid-stat");
      card.appendChild(el("div", "cid-stat-label", label));
      card.appendChild(el("div", "cid-stat-value", String(value)));
      root.appendChild(card);
    });
  }

  function renderTrackList(payload) {
    const root = $("cidTrackList");
    clear(root);
    const wrap = el("div", "cid-list");
    (payload.track_summary?.tracks || []).slice(0, 8).forEach((track) => {
      const card = el("div", "cid-item");
      card.appendChild(el("h4", "", track.title));
      card.appendChild(el("div", "cid-muted", `${track.estimated_hours} hrs • ${track.course_count} courses`));
      const pillWrap = el("div", "");
      (track.focus_tags || []).slice(0, 4).forEach((tag) => pillWrap.appendChild(el("span", "cid-pill", tag)));
      card.appendChild(pillWrap);
      wrap.appendChild(card);
    });
    root.appendChild(wrap);
  }

  function renderHealth(payload) {
    const root = $("cidHealthList");
    clear(root);
    const wrap = el("div", "cid-stack");
    Object.entries(payload.system_health || {}).forEach(([key, value]) => {
      const item = el("div", "cid-item");
      item.appendChild(el("h4", "", key));
      const valueNode = el("div", value === true ? "cid-good" : value === false ? "cid-warn" : "", String(value))
      item.appendChild(valueNode);
      wrap.appendChild(item);
    });
    root.appendChild(wrap);
  }

  function renderMentorPriorities(payload) {
    const root = $("cidMentorPriorities");
    clear(root);
    const wrap = el("div", "cid-stack");
    (payload.mentor_brief?.next_platform_priorities || []).forEach((item) => {
      const card = el("div", "cid-item");
      card.appendChild(el("h3", "", item.priority));
      card.appendChild(el("p", "", item.why));
      wrap.appendChild(card);
    });
    (payload.mentor_brief?.strategic_warnings || []).forEach((warning) => {
      const card = el("div", "cid-item");
      card.appendChild(el("h3", "cid-warn", "Warning"));
      card.appendChild(el("p", "", warning));
      wrap.appendChild(card);
    });
    root.appendChild(wrap);
  }

  function renderBadgeSignals(payload) {
    const root = $("cidBadgeSignals");
    clear(root);
    const wrap = el("div", "cid-stack");
    const badgeCounts = payload.identity_summary?.badge_counts || {};
    const entries = Object.entries(badgeCounts);
    if (!entries.length) {
      const empty = el("div", "cid-item");
      empty.appendChild(el("p", "", "No badges awarded yet. Seed learners or begin using the identity layer."));
      wrap.appendChild(empty);
    } else {
      entries.sort((a, b) => b[1] - a[1]).forEach(([slug, count]) => {
        const card = el("div", "cid-item");
        card.appendChild(el("h4", "", slug));
        card.appendChild(el("div", "cid-muted", `${count} award(s)`));
        wrap.appendChild(card);
      });
    }
    root.appendChild(wrap);
  }

  function renderLearnerPreviews(payload) {
    const root = $("cidLearnerPreviews");
    clear(root);
    const wrap = el("div", "cid-stack");
    const previews = payload.learner_previews || [];
    if (!previews.length) {
      const empty = el("div", "cid-item");
      empty.appendChild(el("p", "", "No learner previews yet. Once learner progress files exist, mentor guidance will appear here."));
      wrap.appendChild(empty);
    } else {
      previews.forEach((preview) => {
        const card = el("div", "cid-item");
        const identity = preview.identity || {};
        card.appendChild(el("h3", "", identity.profile?.display_name || preview.learner_id || "Learner"));
        card.appendChild(el("div", "cid-muted", `Stage: ${preview.momentum_summary?.stage || 'unknown'} • Score: ${preview.momentum_summary?.score || 0}`));
        (preview.recommendations || []).slice(0, 3).forEach((rec) => {
          const block = el("div", "cid-item");
          block.appendChild(el("h4", "", rec.title));
          block.appendChild(el("div", "cid-muted", `${rec.kind} • ${rec.priority}`));
          block.appendChild(el("p", "", rec.action));
          card.appendChild(block);
        });
        wrap.appendChild(card);
      });
    }
    root.appendChild(wrap);
  }

  function renderSummaryObject(targetId, obj) {
    const root = $(targetId);
    clear(root);
    const wrap = el("div", "cid-stack");
    Object.entries(obj || {}).forEach(([key, value]) => {
      const card = el("div", "cid-item");
      card.appendChild(el("h4", "", key));
      card.appendChild(el("div", "cid-muted", String(value)));
      wrap.appendChild(card);
    });
    root.appendChild(wrap);
  }

  function render(payload) {
    $("cidGeneratedAt").textContent = `Generated at ${payload.generated_at || "unknown"}`;
    renderStatGrid(payload);
    renderTrackList(payload);
    renderHealth(payload);
    renderMentorPriorities(payload);
    renderBadgeSignals(payload);
    renderLearnerPreviews(payload);
    renderSummaryObject("cidGraphSummary", payload.graph_summary || {});
    renderSummaryObject("cidMapSummary", payload.map_summary || {});
  }

  async function init() {
    try {
      const payload = await fetchDashboard();
      render(payload);
    } catch (error) {
      console.error(error);
      const root = $("cidLearnerPreviews");
      root.textContent = `Dashboard failed to load. ${error.message}`;
    }
  }

  $("cidReloadButton")?.addEventListener("click", init);
  window.addEventListener("load", init);
})();
