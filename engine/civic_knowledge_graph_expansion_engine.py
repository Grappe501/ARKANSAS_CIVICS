from __future__ import annotations

from pathlib import Path
from datetime import datetime, timezone
from typing import Any
import json
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from engine.platform_kernel import create_kernel  # noqa: E402
from engine.graph_expanders.legislator_graph_expander import LegislatorGraphExpander  # noqa: E402
from engine.graph_expanders.committee_power_expander import CommitteePowerExpander  # noqa: E402
from engine.graph_expanders.donor_influence_expander import DonorInfluenceExpander  # noqa: E402
from engine.graph_expanders.policy_impact_expander import PolicyImpactExpander  # noqa: E402


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


class CivicKnowledgeGraphExpansionEngine:
    """
    Phase 06 — Civic Knowledge Graph Expansion Engine

    Expands civic intelligence into graph-ready nodes and edges for:
    - legislator influence networks
    - committee power mapping
    - donor influence structures
    - policy impact chains
    """

    def __init__(self, root: str | Path | None = None) -> None:
        self.kernel = create_kernel(root)
        self.root = self.kernel.root
        self.source_dir = self.kernel.data_dir / "civic_sources"
        self.processed_dir = self.kernel.data_dir / "civic_processed"
        self.output_dir = self.kernel.ensure_export_dir("graph_expansion")
        self.output_dir.mkdir(parents=True, exist_ok=True)

        self.expanders = [
            LegislatorGraphExpander(),
            CommitteePowerExpander(),
            DonorInfluenceExpander(),
            PolicyImpactExpander(),
        ]

    def build(self) -> dict[str, Any]:
        nodes: list[dict[str, Any]] = []
        edges: list[dict[str, Any]] = []
        reports: list[dict[str, Any]] = []

        for expander in self.expanders:
            print(f"[INFO] Running graph expander: {expander.name}")
            result = expander.expand(
                source_dir=self.source_dir,
                processed_dir=self.processed_dir,
            )
            nodes.extend(result.get("nodes", []))
            edges.extend(result.get("edges", []))
            reports.append({
                "name": expander.name,
                "node_count": len(result.get("nodes", [])),
                "edge_count": len(result.get("edges", [])),
                "source_paths": result.get("source_paths", []),
            })

        payload = {
            "generated_at": utc_now_iso(),
            "engine": "civic_knowledge_graph_expansion_engine",
            "database_connected": False,
            "summary": {
                "node_count": len(nodes),
                "edge_count": len(edges),
                "expander_count": len(self.expanders),
            },
            "reports": reports,
            "nodes": nodes,
            "edges": edges,
        }

        return payload

    def export(self) -> list[Path]:
        payload = self.build()

        json_path = self.output_dir / "civic_graph_expansion.json"
        md_path = self.output_dir / "civic_graph_expansion.md"
        manifest_path = self.output_dir / "civic_graph_manifest.json"

        json_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        md_path.write_text(self.render_markdown(payload), encoding="utf-8")
        manifest_path.write_text(
            json.dumps(
                {
                    "generated_at": utc_now_iso(),
                    "engine": payload["engine"],
                    "summary": payload["summary"],
                    "reports": payload["reports"],
                    "future_uses": [
                        "knowledge graph persistence",
                        "civic intelligence map overlays",
                        "influence scoring",
                        "pathway recommendation",
                        "public explainer generation",
                    ],
                },
                indent=2,
            ),
            encoding="utf-8",
        )

        return [json_path, md_path, manifest_path]

    def render_markdown(self, payload: dict[str, Any]) -> str:
        lines = [
            "# Arkansas Civics Graph Expansion Report",
            "",
            f"- Generated at: `{payload['generated_at']}`",
            f"- Nodes: **{payload['summary']['node_count']}**",
            f"- Edges: **{payload['summary']['edge_count']}**",
            f"- Expanders: **{payload['summary']['expander_count']}**",
            "",
            "## Expander Reports",
            "",
        ]

        for report in payload["reports"]:
            lines.extend([
                f"### {report['name']}",
                f"- Nodes: {report['node_count']}",
                f"- Edges: {report['edge_count']}",
                f"- Sources: {len(report.get('source_paths', []))}",
                "",
            ])

        return "\n".join(lines)
