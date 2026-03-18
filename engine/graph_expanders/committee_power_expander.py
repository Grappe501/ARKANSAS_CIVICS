from __future__ import annotations

from pathlib import Path
from typing import Any
import json


class CommitteePowerExpander:
    name = "Committee Power Maps"

    def expand(self, source_dir: Path, processed_dir: Path) -> dict[str, Any]:
        records = []
        source_paths = []

        committees_path = source_dir / "committees"
        if committees_path.exists():
            for file in sorted(committees_path.glob("*.json")):
                source_paths.append(str(file))
                try:
                    records.append(json.loads(file.read_text(encoding="utf-8")))
                except json.JSONDecodeError:
                    continue

        nodes = []
        edges = []

        for record in records:
            committee_slug = record.get("slug") or record.get("name")
            if not committee_slug:
                continue

            nodes.append({
                "id": f"committee::{committee_slug}",
                "type": "committee",
                "label": record.get("name", committee_slug),
                "metadata": {
                    "jurisdiction": record.get("jurisdiction"),
                    "chamber": record.get("chamber"),
                },
            })

            for bill in record.get("bills", []):
                bill_slug = bill.get("slug") or bill.get("bill_number")
                if not bill_slug:
                    continue

                nodes.append({
                    "id": f"bill::{bill_slug}",
                    "type": "bill",
                    "label": bill.get("bill_number", bill_slug),
                    "metadata": {
                        "title": bill.get("title"),
                        "status": bill.get("status"),
                    },
                })

                edges.append({
                    "source": f"committee::{committee_slug}",
                    "target": f"bill::{bill_slug}",
                    "relationship": "controls_hearing_path",
                    "metadata": {
                        "stage": bill.get("stage"),
                    },
                })

        return {"nodes": nodes, "edges": edges, "source_paths": source_paths}
