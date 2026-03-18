from __future__ import annotations

from pathlib import Path
from typing import Any
import json


class LegislatorGraphExpander:
    name = "Legislator Influence Networks"

    def expand(self, source_dir: Path, processed_dir: Path) -> dict[str, Any]:
        records = []
        source_paths = []

        legislators_path = source_dir / "legislators"
        if legislators_path.exists():
            for file in sorted(legislators_path.glob("*.json")):
                source_paths.append(str(file))
                try:
                    records.append(json.loads(file.read_text(encoding="utf-8")))
                except json.JSONDecodeError:
                    continue

        nodes = []
        edges = []

        for record in records:
            legislator_id = record.get("id") or record.get("slug") or record.get("name")
            if not legislator_id:
                continue

            nodes.append({
                "id": f"legislator::{legislator_id}",
                "type": "legislator",
                "label": record.get("name", legislator_id),
                "metadata": {
                    "district": record.get("district"),
                    "party": record.get("party"),
                    "office": record.get("office"),
                },
            })

            for committee in record.get("committees", []):
                committee_slug = committee.get("slug") or committee.get("name")
                if not committee_slug:
                    continue

                nodes.append({
                    "id": f"committee::{committee_slug}",
                    "type": "committee",
                    "label": committee.get("name", committee_slug),
                    "metadata": {
                        "chamber": committee.get("chamber"),
                    },
                })

                edges.append({
                    "source": f"legislator::{legislator_id}",
                    "target": f"committee::{committee_slug}",
                    "relationship": "serves_on",
                    "metadata": {
                        "role": committee.get("role", "member"),
                    },
                })

        return {"nodes": nodes, "edges": edges, "source_paths": source_paths}
