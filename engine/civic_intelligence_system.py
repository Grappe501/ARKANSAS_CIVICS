from __future__ import annotations

from pathlib import Path
from typing import Any
from datetime import datetime, timezone
import json
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from engine.platform_kernel import create_kernel  # noqa: E402
from engine.civic_intelligence_map import CivicIntelligenceMapEngine  # noqa: E402
from engine.knowledge_graph_engine import KnowledgeGraphEngine  # noqa: E402
from engine.track_engine import TrackEngine  # noqa: E402
from engine.learning_analytics_engine import LearningAnalyticsEngine  # noqa: E402
from engine.user_identity_engine import UserIdentityEngine  # noqa: E402
from engine.civic_mentor_engine import CivicMentorEngine  # noqa: E402


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


class CivicIntelligenceSystem:
    """
    System orchestrator for the Arkansas civic intelligence platform.

    This does not replace the underlying engines. It coordinates them into one
    exportable system snapshot that can power dashboards, admin tooling, and
    future AI layers.
    """

    def __init__(self, root: str | Path | None = None) -> None:
        self.kernel = create_kernel(root)
        self.root = self.kernel.root
        self.map_engine = CivicIntelligenceMapEngine(root)
        self.graph_engine = KnowledgeGraphEngine(root)
        self.track_engine = TrackEngine(root)
        self.analytics_engine = LearningAnalyticsEngine(root)
        self.identity_engine = UserIdentityEngine(root)
        self.mentor_engine = CivicMentorEngine(root)
        self.exports_dir = self.kernel.ensure_export_dir("civic_intelligence")

    def build_system_snapshot(self) -> dict[str, Any]:
        map_payload = self.map_engine.build_map()
        graph_payload = self.graph_engine.build_graph()
        track_defs = [track.to_dict() for track in self.track_engine.build_track_definitions()]
        analytics_payload = self.analytics_engine.build_admin_snapshot()
        identity_index = self.identity_engine.build_platform_identity_index()
        mentor_brief = self.mentor_engine.build_platform_brief()

        learner_previews = []
        for learner in identity_index.get("learners", [])[:20]:
            learner_id = learner.get("learner_id")
            if learner_id:
                learner_previews.append(self.mentor_engine.build_learner_guidance(learner_id))

        snapshot = {
            "generated_at": utc_now_iso(),
            "generated_by": "engine.civic_intelligence_system",
            "project_root": str(self.root),
            "source_of_truth": "content/courses + data/* + exports/*",
            "database_connected": False,
            "system_health": self._build_system_health(
                map_payload,
                graph_payload,
                track_defs,
                analytics_payload,
                identity_index,
            ),
            "map_summary": map_payload.get("summary", {}),
            "graph_summary": graph_payload.get("summary", {}),
            "track_summary": {
                "track_count": len(track_defs),
                "tracks": [
                    {
                        "slug": track["slug"],
                        "title": track["title"],
                        "estimated_hours": track.get("estimated_hours", 0),
                        "course_count": track.get("course_count", 0),
                        "focus_tags": track.get("focus_tags", []),
                    }
                    for track in track_defs
                ],
            },
            "analytics_summary": analytics_payload.get("summary", {}),
            "identity_summary": {
                "learner_count": identity_index.get("learner_count", 0),
                "badge_counts": identity_index.get("badge_counts", {}),
            },
            "mentor_brief": mentor_brief,
            "learner_previews": learner_previews,
        }
        return snapshot

    def _build_system_health(
        self,
        map_payload: dict[str, Any],
        graph_payload: dict[str, Any],
        track_defs: list[dict[str, Any]],
        analytics_payload: dict[str, Any],
        identity_index: dict[str, Any],
    ) -> dict[str, Any]:
        analytics_summary = analytics_payload.get("summary", {})
        return {
            "kernel_ready": True,
            "content_loaded": map_payload.get("summary", {}).get("course_count", 0) > 0,
            "tracks_loaded": len(track_defs) > 0,
            "knowledge_graph_ready": graph_payload.get("summary", {}).get("node_count", 0) > 0,
            "analytics_ready": True,
            "identity_ready": True,
            "mentor_ready": True,
            "learner_count": analytics_summary.get("learner_count", 0),
            "total_active_hours": analytics_summary.get("total_active_hours", 0),
            "badge_count": sum(identity_index.get("badge_counts", {}).values()),
        }

    def export_system(self) -> list[Path]:
        snapshot = self.build_system_snapshot()

        json_path = self.exports_dir / "civic_intelligence_dashboard.json"
        json_path.write_text(json.dumps(snapshot, indent=2), encoding="utf-8")

        md_path = self.exports_dir / "civic_intelligence_system.md"
        md_path.write_text(self.render_markdown(snapshot), encoding="utf-8")

        manifest_path = self.exports_dir / "civic_intelligence_manifest.json"
        manifest = {
            "generated_at": utc_now_iso(),
            "generated_by": "engine.civic_intelligence_system",
            "artifacts": [
                "exports/civic_intelligence/civic_intelligence_dashboard.json",
                "exports/civic_intelligence/civic_intelligence_system.md",
                "exports/analytics/learning_admin_snapshot.json",
                "exports/identity/identity_index.json",
                "exports/mentor/platform_mentor_brief.json",
                "exports/civic_intelligence_map/civic_intelligence_map.json",
                "exports/knowledge_graph/knowledge_graph.json",
            ],
        }
        manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")

        return [json_path, md_path, manifest_path]

    def render_markdown(self, snapshot: dict[str, Any]) -> str:
        lines = [
            "# Arkansas Civic Intelligence System",
            "",
            "This file is generated from the real platform engines and is intended to act as a high-level system briefing.",
            "",
            "## System Health",
            "",
        ]
        for key, value in snapshot.get("system_health", {}).items():
            lines.append(f"- {key}: {value}")

        lines.extend([
            "",
            "## Analytics Summary",
            "",
        ])
        for key, value in snapshot.get("analytics_summary", {}).items():
            lines.append(f"- {key}: {value}")

        lines.extend([
            "",
            "## Tracks",
            "",
        ])
        for track in snapshot.get("track_summary", {}).get("tracks", [])[:10]:
            lines.append(
                f"- **{track['title']}** (`{track['slug']}`) — {track['estimated_hours']} hours, {track['course_count']} courses"
            )

        lines.extend([
            "",
            "## Mentor Priorities",
            "",
        ])
        for item in snapshot.get("mentor_brief", {}).get("next_platform_priorities", []):
            lines.append(f"- **{item['priority']}**: {item['why']}")

        return "\n".join(lines).strip() + "\n"


if __name__ == "__main__":
    engine = CivicIntelligenceSystem()
    outputs = engine.export_system()
    print("\n".join(str(path) for path in outputs))
