from __future__ import annotations

from typing import Any

from .utils import ARKANSAS_JURISDICTION, ensure_dict, stable_uuid


class NodeBuilder:
    """Normalizes raw graph nodes into database-ready records."""

    def build_nodes(self, raw_nodes: list[dict[str, Any]]) -> list[dict[str, Any]]:
        records: list[dict[str, Any]] = []
        for raw in raw_nodes:
            node_type = str(raw.get("type") or raw.get("node_type") or "unknown").strip().lower()
            source_key = str(raw.get("id") or raw.get("key") or raw.get("name") or "unnamed").strip()
            display_name = str(raw.get("name") or source_key).strip()
            metadata = ensure_dict(raw.get("metadata"))

            record = {
                "id": stable_uuid("node", ARKANSAS_JURISDICTION, node_type, source_key),
                "source_key": source_key,
                "jurisdiction": ARKANSAS_JURISDICTION,
                "node_type": node_type,
                "name": display_name,
                "county": raw.get("county"),
                "district": raw.get("district"),
                "chamber": raw.get("chamber"),
                "metadata": {
                    **metadata,
                    "raw": raw,
                },
            }
            records.append(record)
        return records
