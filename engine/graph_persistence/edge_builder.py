from __future__ import annotations

from typing import Any

from .utils import ARKANSAS_JURISDICTION, ensure_dict, stable_uuid


class EdgeBuilder:
    """Normalizes raw graph edges into database-ready relationship rows."""

    def build_edges(
        self,
        raw_edges: list[dict[str, Any]],
        node_lookup: dict[str, dict[str, Any]],
    ) -> list[dict[str, Any]]:
        records: list[dict[str, Any]] = []
        for raw in raw_edges:
            source_key = str(raw.get("source") or raw.get("from") or "").strip()
            target_key = str(raw.get("target") or raw.get("to") or "").strip()
            relationship_type = str(raw.get("relationship") or raw.get("relationship_type") or "related_to").strip().lower()
            weight = raw.get("weight", 1.0)
            metadata = ensure_dict(raw.get("metadata"))

            source_node = node_lookup.get(source_key)
            target_node = node_lookup.get(target_key)
            if not source_node or not target_node:
                continue

            record = {
                "id": stable_uuid(
                    "edge",
                    ARKANSAS_JURISDICTION,
                    source_node["id"],
                    target_node["id"],
                    relationship_type,
                ),
                "jurisdiction": ARKANSAS_JURISDICTION,
                "source_node_id": source_node["id"],
                "target_node_id": target_node["id"],
                "relationship_type": relationship_type,
                "weight": float(weight) if weight is not None else 1.0,
                "metadata": {
                    **metadata,
                    "raw": raw,
                },
            }
            records.append(record)
        return records
