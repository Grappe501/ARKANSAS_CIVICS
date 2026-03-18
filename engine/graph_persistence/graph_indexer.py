from __future__ import annotations

from collections import Counter
from typing import Any


class GraphIndexer:
    """Builds summary/index records for fast reporting and audit visibility."""

    def build_index(
        self,
        nodes: list[dict[str, Any]],
        edges: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        node_counter = Counter(node["node_type"] for node in nodes)
        edge_counter = Counter(edge["relationship_type"] for edge in edges)

        return [
            {
                "index_key": "node_type_counts",
                "index_group": "nodes",
                "payload": dict(node_counter),
            },
            {
                "index_key": "relationship_type_counts",
                "index_group": "edges",
                "payload": dict(edge_counter),
            },
            {
                "index_key": "graph_totals",
                "index_group": "summary",
                "payload": {
                    "node_count": len(nodes),
                    "edge_count": len(edges),
                },
            },
        ]
