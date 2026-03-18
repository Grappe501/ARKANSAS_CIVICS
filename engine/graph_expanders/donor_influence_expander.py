from __future__ import annotations

from pathlib import Path
from typing import Any
import json


class DonorInfluenceExpander:
    name = "Donor Influence Graphs"

    def expand(self, source_dir: Path, processed_dir: Path) -> dict[str, Any]:
        records = []
        source_paths = []

        donors_path = source_dir / "donors"
        if donors_path.exists():
            for file in sorted(donors_path.glob("*.json")):
                source_paths.append(str(file))
                try:
                    records.append(json.loads(file.read_text(encoding="utf-8")))
                except json.JSONDecodeError:
                    continue

        nodes = []
        edges = []

        for record in records:
            donor_slug = record.get("slug") or record.get("name")
            recipient_slug = record.get("recipient_slug") or record.get("recipient_name")
            amount = record.get("amount", 0)

            if donor_slug:
                nodes.append({
                    "id": f"donor::{donor_slug}",
                    "type": "donor",
                    "label": record.get("name", donor_slug),
                    "metadata": {
                        "industry": record.get("industry"),
                        "location": record.get("location"),
                    },
                })

            if recipient_slug:
                nodes.append({
                    "id": f"recipient::{recipient_slug}",
                    "type": "recipient",
                    "label": record.get("recipient_name", recipient_slug),
                    "metadata": {
                        "office": record.get("office"),
                        "district": record.get("district"),
                    },
                })

            if donor_slug and recipient_slug:
                edges.append({
                    "source": f"donor::{donor_slug}",
                    "target": f"recipient::{recipient_slug}",
                    "relationship": "funds",
                    "metadata": {
                        "amount": amount,
                        "cycle": record.get("cycle"),
                    },
                })

        return {"nodes": nodes, "edges": edges, "source_paths": source_paths}
