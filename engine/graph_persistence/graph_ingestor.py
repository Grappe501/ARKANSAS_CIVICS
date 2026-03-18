from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .edge_builder import EdgeBuilder
from .graph_indexer import GraphIndexer
from .node_builder import NodeBuilder
from .utils import load_json, write_json


@dataclass
class GraphPayload:
    nodes: list[dict[str, Any]]
    edges: list[dict[str, Any]]
    indexes: list[dict[str, Any]]
    source_path: str


class GraphIngestor:
    """Converts Phase 06 graph exports into normalized Phase 07 records."""

    def __init__(self) -> None:
        self.node_builder = NodeBuilder()
        self.edge_builder = EdgeBuilder()
        self.graph_indexer = GraphIndexer()

    def load_and_normalize(self, graph_path: str | Path) -> GraphPayload:
        raw = load_json(graph_path)
        raw_nodes = raw.get("nodes") or raw.get("graph", {}).get("nodes") or []
        raw_edges = raw.get("edges") or raw.get("graph", {}).get("edges") or []

        nodes = self.node_builder.build_nodes(raw_nodes)
        node_lookup = {node["source_key"]: node for node in nodes}
        edges = self.edge_builder.build_edges(raw_edges, node_lookup)
        indexes = self.graph_indexer.build_index(nodes, edges)

        return GraphPayload(
            nodes=nodes,
            edges=edges,
            indexes=indexes,
            source_path=str(graph_path),
        )

    def write_build_artifacts(self, payload: GraphPayload, export_dir: str | Path) -> dict[str, str]:
        export_dir = Path(export_dir)
        export_dir.mkdir(parents=True, exist_ok=True)

        paths = {
            "nodes": str(export_dir / "phase_07_nodes.json"),
            "edges": str(export_dir / "phase_07_edges.json"),
            "indexes": str(export_dir / "phase_07_indexes.json"),
            "manifest": str(export_dir / "phase_07_build_manifest.json"),
        }

        write_json(paths["nodes"], {"rows": payload.nodes, "count": len(payload.nodes)})
        write_json(paths["edges"], {"rows": payload.edges, "count": len(payload.edges)})
        write_json(paths["indexes"], {"rows": payload.indexes, "count": len(payload.indexes)})
        write_json(
            paths["manifest"],
            {
                "phase": "07",
                "name": "civic_graph_persistence",
                "source_graph": payload.source_path,
                "counts": {
                    "nodes": len(payload.nodes),
                    "edges": len(payload.edges),
                    "indexes": len(payload.indexes),
                },
            },
        )
        return paths
