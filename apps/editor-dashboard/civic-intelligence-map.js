(() => {
  "use strict";

  const MAP_URL = "../../exports/civic_intelligence_map/civic_intelligence_map.json";

  const state = {
    payload: null,
    selectedNodeId: null,
    search: "",
    filterType: "all",
    zoom: 1,
    panX: 0,
    panY: 0,
    dragging: false,
    dragStartX: 0,
    dragStartY: 0,
    dragOriginX: 0,
    dragOriginY: 0,
  };

  const COLORS = {
    track: "#8b5cf6",
    course: "#38bdf8",
    chapter: "#22c55e",
    segment: "#f59e0b",
  };

  function q(id) {
    return document.getElementById(id);
  }

  function clear(node) {
    while (node.firstChild) node.removeChild(node.firstChild);
  }

  function el(tag, cls = "", text = "") {
    const node = document.createElement(tag);
    if (cls) node.className = cls;
    if (text) node.textContent = text;
    return node;
  }

  function safeArray(value) {
    return Array.isArray(value) ? value : [];
  }

  async function fetchJson(url) {
    const response = await fetch(url, { cache: "no-store" });
    if (!response.ok) throw new Error(`Failed to load ${url} (${response.status})`);
    return response.json();
  }

  async function loadMap() {
    const root = q("civic-intelligence-map-root");
    if (!root) return;
    root.innerHTML = "Loading civic intelligence map…";

    try {
      const payload = await fetchJson(MAP_URL);
      state.payload = payload;
      const firstNode = safeArray(payload.nodes)[0];
      state.selectedNodeId = firstNode ? firstNode.id : null;
      render();
    } catch (error) {
      console.error(error);
      root.innerHTML = `Failed to load civic intelligence map. ${error.message}`;
    }
  }

  function filteredNodes() {
    if (!state.payload) return [];
    const query = String(state.search || "").trim().toLowerCase();
    return safeArray(state.payload.nodes).filter((node) => {
      if (state.filterType !== "all" && node.node_type !== state.filterType) return false;
      if (!query) return true;
      const haystack = `${node.label} ${node.slug} ${node.source_path || ""}`.toLowerCase();
      return haystack.includes(query);
    });
  }

  function edgesForVisible(visibleSet) {
    if (!state.payload) return [];
    return safeArray(state.payload.edges).filter(
      (edge) => visibleSet.has(edge.source) && visibleSet.has(edge.target)
    );
  }

  function getSelectedNode() {
    if (!state.payload || !state.selectedNodeId) return null;
    return safeArray(state.payload.nodes).find((node) => node.id === state.selectedNodeId) || null;
  }

  function computeLayout(nodes) {
    const levels = new Map();
    nodes.forEach((node) => {
      if (!levels.has(node.level)) levels.set(node.level, []);
      levels.get(node.level).push(node);
    });

    const positions = new Map();
    const levelKeys = [...levels.keys()].sort((a, b) => a - b);
    const xGap = 300;
    const yGap = 110;

    levelKeys.forEach((level) => {
      const bucket = levels.get(level) || [];
      bucket.forEach((node, index) => {
        positions.set(node.id, {
          x: 160 + level * xGap,
          y: 100 + index * yGap,
          width: 220,
          height: 72,
        });
      });
    });

    return positions;
  }

  function render() {
    const root = q("civic-intelligence-map-root");
    if (!root) return;
    clear(root);

    if (!state.payload) {
      root.textContent = "Map not loaded.";
      return;
    }

    const shell = el("div", "civic-map-shell");
    shell.appendChild(renderSidebar());
    shell.appendChild(renderCanvas());
    shell.appendChild(renderInspector());
    root.appendChild(shell);
  }

  function renderSidebar() {
    const sidebar = el("div", "civic-map-sidebar");
    sidebar.appendChild(el("h3", "", "Civic Intelligence Map"));

    const summary = state.payload.summary || {};
    const stats = el("div", "civic-map-stats");
    [
      ["Tracks", summary.track_count || 0],
      ["Courses", summary.course_count || 0],
      ["Chapters", summary.chapter_count || 0],
      ["Segments", summary.segment_count || 0],
      ["Edges", summary.edge_count || 0],
    ].forEach(([label, value]) => {
      const row = el("div", "civic-map-stat-row");
      row.appendChild(el("span", "civic-map-stat-label", label));
      row.appendChild(el("strong", "civic-map-stat-value", String(value)));
      stats.appendChild(row);
    });
    sidebar.appendChild(stats);

    const search = document.createElement("input");
    search.type = "search";
    search.className = "civic-map-search";
    search.placeholder = "Search the graph…";
    search.value = state.search;
    search.addEventListener("input", (event) => {
      state.search = event.target.value || "";
      render();
    });
    sidebar.appendChild(search);

    const filter = document.createElement("select");
    filter.className = "civic-map-filter";
    ["all", "track", "course", "chapter", "segment"].forEach((value) => {
      const option = document.createElement("option");
      option.value = value;
      option.textContent = value === "all" ? "All Node Types" : value;
      if (value === state.filterType) option.selected = true;
      filter.appendChild(option);
    });
    filter.addEventListener("change", (event) => {
      state.filterType = event.target.value;
      render();
    });
    sidebar.appendChild(filter);

    const list = el("div", "civic-map-list");
    filteredNodes().slice(0, 120).forEach((node) => {
      const button = el("button", "civic-map-list-item", `${node.label}`);
      if (node.id === state.selectedNodeId) button.classList.add("active");
      button.addEventListener("click", () => {
        state.selectedNodeId = node.id;
        render();
      });
      const meta = el("div", "civic-map-list-meta", `${node.node_type} • ${node.slug}`);
      button.appendChild(meta);
      list.appendChild(button);
    });
    sidebar.appendChild(list);
    return sidebar;
  }

  function renderCanvas() {
    const wrapper = el("div", "civic-map-canvas-wrap");

    const toolbar = el("div", "civic-map-canvas-toolbar");
    const zoomIn = el("button", "", "+");
    const zoomOut = el("button", "", "−");
    const reset = el("button", "", "Reset View");

    zoomIn.addEventListener("click", () => {
      state.zoom = Math.min(2.5, state.zoom + 0.1);
      render();
    });
    zoomOut.addEventListener("click", () => {
      state.zoom = Math.max(0.5, state.zoom - 0.1);
      render();
    });
    reset.addEventListener("click", () => {
      state.zoom = 1;
      state.panX = 0;
      state.panY = 0;
      render();
    });

    toolbar.appendChild(zoomOut);
    toolbar.appendChild(zoomIn);
    toolbar.appendChild(reset);
    wrapper.appendChild(toolbar);

    const viewport = el("div", "civic-map-viewport");
    const svgNS = "http://www.w3.org/2000/svg";
    const svg = document.createElementNS(svgNS, "svg");
    svg.setAttribute("class", "civic-map-svg");
    svg.setAttribute("viewBox", "0 0 1400 1200");

    const visibleNodes = filteredNodes();
    const visibleSet = new Set(visibleNodes.map((node) => node.id));
    const visibleEdges = edgesForVisible(visibleSet);
    const positions = computeLayout(visibleNodes);

    const graph = document.createElementNS(svgNS, "g");
    graph.setAttribute("transform", `translate(${state.panX} ${state.panY}) scale(${state.zoom})`);

    visibleEdges.forEach((edge) => {
      const source = positions.get(edge.source);
      const target = positions.get(edge.target);
      if (!source || !target) return;
      const line = document.createElementNS(svgNS, "line");
      line.setAttribute("x1", String(source.x + source.width));
      line.setAttribute("y1", String(source.y + source.height / 2));
      line.setAttribute("x2", String(target.x));
      line.setAttribute("y2", String(target.y + target.height / 2));
      line.setAttribute("stroke", "rgba(148,163,184,0.35)");
      line.setAttribute("stroke-width", "2");
      graph.appendChild(line);
    });

    visibleNodes.forEach((node) => {
      const pos = positions.get(node.id);
      if (!pos) return;

      const nodeGroup = document.createElementNS(svgNS, "g");
      nodeGroup.setAttribute("class", "civic-map-node-group");
      nodeGroup.style.cursor = "pointer";
      nodeGroup.addEventListener("click", () => {
        state.selectedNodeId = node.id;
        render();
      });

      const rect = document.createElementNS(svgNS, "rect");
      rect.setAttribute("x", String(pos.x));
      rect.setAttribute("y", String(pos.y));
      rect.setAttribute("width", String(pos.width));
      rect.setAttribute("height", String(pos.height));
      rect.setAttribute("rx", "16");
      rect.setAttribute("fill", "rgba(15,23,42,0.9)");
      rect.setAttribute("stroke", COLORS[node.node_type] || "#38bdf8");
      rect.setAttribute("stroke-width", node.id === state.selectedNodeId ? "3" : "1.5");
      nodeGroup.appendChild(rect);

      const label = document.createElementNS(svgNS, "text");
      label.setAttribute("x", String(pos.x + 16));
      label.setAttribute("y", String(pos.y + 28));
      label.setAttribute("fill", "#e2e8f0");
      label.setAttribute("font-size", "16");
      label.setAttribute("font-weight", "700");
      label.textContent = node.label.slice(0, 28);
      nodeGroup.appendChild(label);

      const meta = document.createElementNS(svgNS, "text");
      meta.setAttribute("x", String(pos.x + 16));
      meta.setAttribute("y", String(pos.y + 52));
      meta.setAttribute("fill", "#94a3b8");
      meta.setAttribute("font-size", "12");
      meta.textContent = `${node.node_type} • ${node.slug}`.slice(0, 34);
      nodeGroup.appendChild(meta);

      graph.appendChild(nodeGroup);
    });

    svg.appendChild(graph);
    enablePan(svg);
    viewport.appendChild(svg);
    wrapper.appendChild(viewport);
    return wrapper;
  }

  function enablePan(svg) {
    svg.addEventListener("mousedown", (event) => {
      state.dragging = true;
      state.dragStartX = event.clientX;
      state.dragStartY = event.clientY;
      state.dragOriginX = state.panX;
      state.dragOriginY = state.panY;
    });

    window.addEventListener("mousemove", (event) => {
      if (!state.dragging) return;
      state.panX = state.dragOriginX + (event.clientX - state.dragStartX);
      state.panY = state.dragOriginY + (event.clientY - state.dragStartY);
      const graph = svg.querySelector("g");
      if (graph) graph.setAttribute("transform", `translate(${state.panX} ${state.panY}) scale(${state.zoom})`);
    });

    window.addEventListener("mouseup", () => {
      state.dragging = false;
    });
  }

  function renderInspector() {
    const inspector = el("div", "civic-map-inspector");
    inspector.appendChild(el("h3", "", "Inspector"));

    const node = getSelectedNode();
    if (!node) {
      inspector.appendChild(el("div", "civic-map-empty", "Select a node to inspect its details."));
      return inspector;
    }

    inspector.appendChild(metaRow("Label", node.label));
    inspector.appendChild(metaRow("Type", node.node_type));
    inspector.appendChild(metaRow("Slug", node.slug));
    inspector.appendChild(metaRow("Source Path", node.source_path || "None"));
    inspector.appendChild(metaRow("Parent", node.parent_id || "None"));
    inspector.appendChild(metaRow("Level", String(node.level)));

    const metadata = node.metadata || {};
    Object.entries(metadata).forEach(([key, value]) => {
      inspector.appendChild(metaRow(key, typeof value === "object" ? JSON.stringify(value) : String(value)));
    });

    return inspector;
  }

  function metaRow(label, value) {
    const row = el("div", "civic-map-meta-row");
    row.appendChild(el("div", "civic-map-meta-label", label));
    row.appendChild(el("div", "civic-map-meta-value", value));
    return row;
  }

  window.ArkansasCivicsCivicMap = { reload: loadMap, state };
  window.addEventListener("load", loadMap);
})();
