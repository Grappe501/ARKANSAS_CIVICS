from __future__ import annotations

from pathlib import Path
from typing import Any
import json


class PolicyImpactExpander:
    name = "Policy Impact Chains"

    def expand(self, source_dir: Path, processed_dir: Path) -> dict[str, Any]:
        records = []
        source_paths = []

        impacts_path = source_dir / "policy_impacts"
        if impacts_path.exists():
            for file in sorted(impacts_path.glob("*.json")):
                source_paths.append(str(file))
                try:
                    records.append(json.loads(file.read_text(encoding="utf-8")))
                except json.JSONDecodeError:
                    continue

        nodes = []
        edges = []

        for record in records:
            policy_slug = record.get("slug") or record.get("policy_name")
            community_slug = record.get("community_slug") or record.get("community_name")

            if policy_slug:
                nodes.append({
                    "id": f"policy::{policy_slug}",
                    "type": "policy",
                    "label": record.get("policy_name", policy_slug),
                    "metadata": {
                        "issue_area": record.get("issue_area"),
                        "status": record.get("status"),
                    },
                })

            if community_slug:
                nodes.append({
                    "id": f"community::{community_slug}",
                    "type": "community",
                    "label": record.get("community_name", community_slug),
                    "metadata": {
                        "region": record.get("region"),
                        "population_focus": record.get("population_focus"),
                    },
                })

            if policy_slug and community_slug:
                edges.append({
                    "source": f"policy::{policy_slug}",
                    "target": f"community::{community_slug}",
                    "relationship": "impacts",
                    "metadata": {
                        "impact_type": record.get("impact_type"),
                        "severity": record.get("severity"),
                    },
                })

        return {"nodes": nodes, "edges": edges, "source_paths": source_paths}
