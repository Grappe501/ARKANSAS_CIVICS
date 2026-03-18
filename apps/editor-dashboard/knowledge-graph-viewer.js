(() => {
  "use strict";

  const GRAPH_URL = "../../exports/knowledge_graph/knowledge_graph.json";

  const state = {
    graph: null,
    query: "",
    filter: "all",
    selectedNodeId: null,
    error: null,
  };

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

  async function loadGraph() {
    try {
      const response = await fetch(GRAPH_URL, { cache: "no-store" });
      if (!response.ok) throw new Error(`Request failed (${response.status})`);
      state.graph = await response.json();
      state.selectedNodeId = state.graph.nodes?.[0]?.id || null;
      render();
    } catch (error) {
      console.error(error);
      state.error = `Failed to load knowledge graph. ${error.message}`;
      render();
    }
  }

  function filteredNodes() {
    const nodes = state.graph?.nodes || [];
    const q = state.query.trim().toLowerCase();
    return nodes.filter((node) => {
      const matchesType = state.filter === "all" || node.node_type === state.filter;
      const haystack = `${node.label} ${node.id} ${JSON.stringify(node.metadata || {})}`.toLowerCase();
      const matchesQuery = !q || haystack.includes(q);
      return matchesType && matchesQuery;
    });
  }

  function selectedNode() {
    return (state.graph?.nodes || []).find((node) => node.id === state.selectedNodeId) || null;
  }

  function relatedEdges(nodeId) {
    return (state.graph?.edges || []).filter((edge) => edge.source === nodeId || edge.target === nodeId);
  }

  function render() {
    const root = $("knowledge-graph-view");
    if (!root) return;
    clear(root);

    if (state.error) {
      root.appendChild(el("div", "course-engine-error", state.error));
      return;
    }

    if (!state.graph) {
      root.appendChild(el("div", "course-engine-empty", "Loading knowledge graph…"));
      return;
    }

    const shell = el("div", "course-engine-shell knowledge-graph-shell");
    const sidebar = el("div", "course-engine-sidebar knowledge-graph-sidebar");
    const main = el("div", "course-engine-main knowledge-graph-main");

    const toolbar = el("div", "course-engine-toolbar");
    const search = document.createElement("input");
    search.className = "course-engine-search";
    search.placeholder = "Search concepts, courses, tags…";
    search.value = state.query;
    search.addEventListener("input", (e) => {
      state.query = e.target.value || "";
      render();
    });

    const filter = document.createElement("select");
    filter.className = "course-engine-search";
    ["all", "track", "course", "chapter", "segment", "concept", "tag"].forEach((value) => {
      const option = document.createElement("option");
      option.value = value;
      option.textContent = value === "all" ? "All Node Types" : value;
      if (state.filter === value) option.selected = true;
      filter.appendChild(option);
    });
    filter.addEventListener("change", (e) => {
      state.filter = e.target.value || "all";
      render();
    });

    toolbar.appendChild(search);
    toolbar.appendChild(filter);
    sidebar.appendChild(toolbar);

    const stats = el("div", "course-engine-stats");
    const summary = state.graph.summary || {};
    [
      ["Nodes", summary.node_count || 0],
      ["Edges", summary.edge_count || 0],
      ["Concepts", summary.concept_count || 0],
      ["Tags", summary.tag_count || 0],
    ].forEach(([label, value]) => {
      const row = el("div", "course-engine-stat");
      row.appendChild(el("div", "course-engine-stat-label", label));
      row.appendChild(el("div", "course-engine-stat-value", String(value)));
      stats.appendChild(row);
    });
    sidebar.appendChild(stats);

    const list = el("div", "course-engine-list");
    filteredNodes().slice(0, 400).forEach((node) => {
      const card = el("button", "course-engine-card");
      card.type = "button";
      if (node.id === state.selectedNodeId) card.classList.add("course-engine-card--active");
      card.appendChild(el("div", "course-engine-card-title", node.label));
      card.appendChild(el("div", "course-engine-card-meta", `${node.node_type} • ${node.id}`));
      card.addEventListener("click", () => {
        state.selectedNodeId = node.id;
        render();
      });
      list.appendChild(card);
    });
    sidebar.appendChild(list);

    const node = selectedNode();
    if (!node) {
      main.appendChild(el("div", "course-engine-empty", "Select a node to inspect its relationships."));
    } else {
      const detail = el("div", "course-engine-detail");
      const section = el("div", "course-engine-section");
      section.appendChild(el("h2", "course-engine-detail-title", node.label));
      section.appendChild(el("div", "course-engine-detail-subtitle", `${node.node_type} • ${node.id}`));

      const meta = el("div", "course-engine-meta");
      Object.entries(node.metadata || {}).forEach(([key, value]) => {
        const line = el("div", "course-engine-meta-line");
        const strong = document.createElement("strong");
        strong.textContent = `${key}: `;
        line.appendChild(strong);
        line.appendChild(document.createTextNode(typeof value === "object" ? JSON.stringify(value) : String(value)));
        meta.appendChild(line);
      });
      section.appendChild(meta);
      detail.appendChild(section);

      const edgesSection = el("div", "course-engine-section");
      edgesSection.appendChild(el("h3", "", "Relationships"));
      const edgesWrap = el("div", "course-engine-stack");
      relatedEdges(node.id).forEach((edge) => {
        const panel = el("div", "course-engine-panel");
        panel.appendChild(el("div", "course-engine-panel-title", `${edge.source} → ${edge.target}`));
        panel.appendChild(el("div", "course-engine-panel-meta", `Relation: ${edge.relation}`));
        edgesWrap.appendChild(panel);
      });
      if (!edgesWrap.childNodes.length) {
        edgesWrap.appendChild(el("div", "course-engine-empty", "No related edges found."));
      }
      edgesSection.appendChild(edgesWrap);
      detail.appendChild(edgesSection);
      main.appendChild(detail);
    }

    shell.appendChild(sidebar);
    shell.appendChild(main);
    root.appendChild(shell);
  }

  window.ArkansasCivicsKnowledgeGraphViewer = { reload: loadGraph };
  window.addEventListener("load", loadGraph);
})();
