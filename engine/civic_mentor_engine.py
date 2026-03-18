from __future__ import annotations

from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any
from datetime import datetime, timezone
import json
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from engine.platform_kernel import create_kernel  # noqa: E402
from engine.track_engine import TrackEngine  # noqa: E402
from engine.knowledge_graph_engine import KnowledgeGraphEngine  # noqa: E402
from engine.user_identity_engine import UserIdentityEngine  # noqa: E402
from engine.learning_analytics_engine import LearningAnalyticsEngine  # noqa: E402


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass
class MentorRecommendation:
    title: str
    kind: str
    priority: str
    why: str
    action: str
    metadata: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class CivicMentorEngine:
    """
    Advisory layer that turns platform state into civic coaching.

    Design goals:
    - no external API dependency
    - use real platform engines and file outputs
    - produce learner guidance and platform-level strategic signals
    - remain deterministic so it can be audited and improved later
    """

    def __init__(self, root: str | Path | None = None) -> None:
        self.kernel = create_kernel(root)
        self.root = self.kernel.root
        self.track_engine = TrackEngine(root)
        self.graph_engine = KnowledgeGraphEngine(root)
        self.identity_engine = UserIdentityEngine(root)
        self.analytics_engine = LearningAnalyticsEngine(root)
        self.exports_dir = self.kernel.exports_dir / "mentor"
        self.exports_dir.mkdir(parents=True, exist_ok=True)

    # ---------------------------------------------------------
    # learner-facing mentorship
    # ---------------------------------------------------------

    def build_learner_guidance(self, learner_id: str) -> dict[str, Any]:
        identity = self.identity_engine.build_identity_snapshot(learner_id)
        analytics = identity.get("analytics_summary", {})
        graph = self.graph_engine.build_graph()
        tracks = self.track_engine.build_track_definitions()

        recommendations = self._build_recommendations(identity, analytics, graph, tracks)
        coaching_questions = self._build_coaching_questions(identity, analytics)
        momentum_summary = self._build_momentum_summary(identity, analytics)

        payload = {
            "generated_at": utc_now_iso(),
            "generated_by": "engine.civic_mentor_engine",
            "learner_id": learner_id,
            "identity": identity,
            "momentum_summary": momentum_summary,
            "recommendations": [item.to_dict() for item in recommendations],
            "coaching_questions": coaching_questions,
        }

        output_path = self.exports_dir / f"{learner_id}_mentor_guidance.json"
        output_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        return payload

    def _build_recommendations(
        self,
        identity: dict[str, Any],
        analytics: dict[str, Any],
        graph: dict[str, Any],
        tracks: list[Any],
    ) -> list[MentorRecommendation]:
        recs: list[MentorRecommendation] = []

        readiness = identity.get("readiness", {})
        recommended_tracks = identity.get("recommended_tracks", [])
        role_signals = identity.get("role_signals", [])
        profile = identity.get("profile", {})

        active_hours = float(analytics.get("active_hours", 0.0))
        volunteer_hours = float(analytics.get("volunteer_hours", 0.0))
        completed_segments = int(analytics.get("total_completed_segments", 0))
        course_rollups = analytics.get("course_rollups", {}) or {}

        if active_hours < 1:
            recs.append(
                MentorRecommendation(
                    title="Establish your first civic study rhythm",
                    kind="study-habit",
                    priority="high",
                    why="The system sees little or no active learning time yet.",
                    action="Complete a foundation lesson this week and stay in active mode for at least 45 focused minutes.",
                    metadata={"active_hours": active_hours},
                )
            )

        if completed_segments < 3:
            recs.append(
                MentorRecommendation(
                    title="Turn reading into completion",
                    kind="completion",
                    priority="high",
                    why="Momentum is easier to keep once a few segments are fully completed.",
                    action="Choose one course path and complete at least three segments before switching topics.",
                    metadata={"completed_segments": completed_segments},
                )
            )

        if volunteer_hours < 2:
            recs.append(
                MentorRecommendation(
                    title="Bridge the platform to the real world",
                    kind="field-activation",
                    priority="medium",
                    why="Civic intelligence grows faster when learning is paired with public action.",
                    action="Log one real-world volunteer activity: canvass, meeting attendance, call time, mutual aid, or community outreach.",
                    metadata={"volunteer_hours": volunteer_hours},
                )
            )

        if recommended_tracks:
            top_track = recommended_tracks[0]
            recs.append(
                MentorRecommendation(
                    title=f"Commit to {top_track['title']}",
                    kind="track-selection",
                    priority="high",
                    why="This is the strongest pathway match based on learning behavior, role signals, and interests.",
                    action=f"Adopt {top_track['title']} as your primary lane and begin its first milestone.",
                    metadata={"track_slug": top_track["track_slug"], "score": top_track["score"]},
                )
            )

        if role_signals:
            top_role = role_signals[0]
            recs.append(
                MentorRecommendation(
                    title=f"Develop your {top_role['role']} lane",
                    kind="role-development",
                    priority="medium",
                    why="This role currently shows the strongest alignment with your learning pattern.",
                    action="Focus your next courses, volunteer experiences, and leadership tasks around this specialty.",
                    metadata={"role": top_role["role"], "score": top_role["score"]},
                )
            )

        top_course = None
        if course_rollups:
            top_course = max(
                course_rollups.items(),
                key=lambda item: float(item[1].get("active_hours", 0.0)),
            )
        if top_course:
            recs.append(
                MentorRecommendation(
                    title="Exploit the learner's strongest momentum zone",
                    kind="momentum",
                    priority="medium",
                    why=f"{top_course[0]} currently has the learner's highest engagement.",
                    action="Use the course with the strongest momentum as the anchor path for the next week of study.",
                    metadata={"course_slug": top_course[0], "active_hours": top_course[1].get("active_hours", 0.0)},
                )
            )

        concept_count = graph.get("summary", {}).get("concept_count", 0)
        if concept_count > 0 and readiness.get("score", 0) >= 60:
            recs.append(
                MentorRecommendation(
                    title="Move from course consumption to systems thinking",
                    kind="systems-thinking",
                    priority="medium",
                    why="The learner has enough progress to start connecting concepts across courses.",
                    action="Use the knowledge graph and civic map to connect campaign work, Arkansas history, narrative, and direct democracy as one system.",
                    metadata={"concept_count": concept_count},
                )
            )

        return recs[:6]

    def _build_momentum_summary(self, identity: dict[str, Any], analytics: dict[str, Any]) -> dict[str, Any]:
        readiness = identity.get("readiness", {})
        role_signals = identity.get("role_signals", [])
        top_role = role_signals[0]["role"] if role_signals else None
        return {
            "stage": readiness.get("stage", "onboarding"),
            "score": readiness.get("score", 0),
            "top_role_signal": top_role,
            "active_hours": analytics.get("active_hours", 0),
            "volunteer_hours": analytics.get("volunteer_hours", 0),
            "completed_segments": analytics.get("total_completed_segments", 0),
        }

    def _build_coaching_questions(self, identity: dict[str, Any], analytics: dict[str, Any]) -> list[str]:
        role_signals = identity.get("role_signals", [])
        active_hours = float(analytics.get("active_hours", 0.0))
        questions = [
            "Where does power actually live in the issue area you care about most?",
            "What skill are you building right now that directly changes your usefulness to a team?",
            "What piece of your learning still has not been tested in the real world?",
        ]
        if role_signals:
            questions.append(f"What would it take to become undeniably reliable as a {role_signals[0]['role']}?")
        if active_hours < 5:
            questions.append("What weekly routine would make civic learning automatic instead of occasional?")
        else:
            questions.append("Which advanced track should you commit to before you spread yourself too thin?")
        return questions[:5]

    # ---------------------------------------------------------
    # platform-facing mentorship
    # ---------------------------------------------------------

    def build_platform_brief(self) -> dict[str, Any]:
        analytics = self.analytics_engine.build_admin_snapshot()
        identity_index = self.identity_engine.build_platform_identity_index()
        tracks = [track.to_dict() for track in self.track_engine.build_track_definitions()]
        graph = self.graph_engine.build_graph()

        learner_count = analytics.get("summary", {}).get("learner_count", 0)
        total_active_hours = analytics.get("summary", {}).get("total_active_hours", 0)

        strategic_warnings: list[str] = []
        if learner_count == 0:
            strategic_warnings.append("No learner progress files exist yet. The platform has infrastructure but not user momentum.")
        if total_active_hours == 0:
            strategic_warnings.append("Learning analytics show zero active hours. Seed demo learners or connect the runtime to real users.")
        if graph.get("summary", {}).get("concept_count", 0) < 100:
            strategic_warnings.append("Knowledge graph concept density is still shallow for a full civic intelligence system.")

        priorities = [
            {
                "priority": "identity-and-auth",
                "why": "The platform now has analytics and guidance, but still needs a formal user account layer to scale.",
            },
            {
                "priority": "dashboard-integration",
                "why": "The system now generates cross-engine exports that should be surfaced in the editor dashboard.",
            },
            {
                "priority": "runtime-events",
                "why": "The biggest unlock now is wiring real learner events from the lesson player into analytics and mentorship loops.",
            },
            {
                "priority": "regional-intelligence-layer",
                "why": "A full civic intelligence system should eventually connect courses to counties, districts, officeholders, and legislation.",
            },
        ]

        payload = {
            "generated_at": utc_now_iso(),
            "generated_by": "engine.civic_mentor_engine",
            "platform_summary": {
                "learner_count": learner_count,
                "total_active_hours": total_active_hours,
                "track_count": len(tracks),
                "knowledge_graph_nodes": graph.get("summary", {}).get("node_count", 0),
            },
            "strategic_warnings": strategic_warnings,
            "next_platform_priorities": priorities,
        }

        path = self.exports_dir / "platform_mentor_brief.json"
        path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        return payload


if __name__ == "__main__":
    engine = CivicMentorEngine()
    print(json.dumps(engine.build_platform_brief(), indent=2))
