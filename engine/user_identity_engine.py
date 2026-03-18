from __future__ import annotations

from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Any
from datetime import datetime, timezone
import json
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from engine.platform_kernel import create_kernel  # noqa: E402
from engine.learning_analytics_engine import LearningAnalyticsEngine  # noqa: E402
from engine.track_engine import TrackEngine  # noqa: E402


DEFAULT_INTERESTS = [
    "arkansas-civics",
    "organizing",
    "leadership",
    "public-service",
]


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass
class BadgeAward:
    badge_slug: str
    title: str
    description: str
    awarded_at: str
    source: str
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class LearnerProfile:
    learner_id: str
    display_name: str
    email: str = ""
    home_region: str = "Arkansas"
    organization: str = ""
    bio: str = ""
    interests: list[str] = field(default_factory=lambda: list(DEFAULT_INTERESTS))
    target_roles: list[str] = field(default_factory=list)
    civic_goals: list[str] = field(default_factory=list)
    badges: list[BadgeAward] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)
    created_at: str = field(default_factory=utc_now_iso)
    updated_at: str = field(default_factory=utc_now_iso)

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["badges"] = [badge.to_dict() for badge in self.badges]
        return payload


class UserIdentityEngine:
    """
    File-backed identity and readiness layer for the civic intelligence system.

    Responsibilities:
    - maintain learner profiles and goal metadata
    - infer readiness and role signals from analytics + track definitions
    - award lightweight badges without requiring a database
    - export identity snapshots that the dashboard and mentor can consume
    """

    def __init__(self, root: str | Path | None = None) -> None:
        self.kernel = create_kernel(root)
        self.root = self.kernel.root
        self.analytics_engine = LearningAnalyticsEngine(root)
        self.track_engine = TrackEngine(root)

        self.identity_dir = self.kernel.data_dir / "identity"
        self.learners_dir = self.identity_dir / "learners"
        self.exports_dir = self.kernel.exports_dir / "identity"

        self.identity_dir.mkdir(parents=True, exist_ok=True)
        self.learners_dir.mkdir(parents=True, exist_ok=True)
        self.exports_dir.mkdir(parents=True, exist_ok=True)

    # ---------------------------------------------------------
    # paths and profile persistence
    # ---------------------------------------------------------

    def learner_profile_path(self, learner_id: str) -> Path:
        safe = learner_id.replace("/", "_").replace("\\", "_")
        return self.learners_dir / f"{safe}_profile.json"

    def load_profile(self, learner_id: str) -> LearnerProfile:
        path = self.learner_profile_path(learner_id)
        if not path.exists():
            return self.create_profile(learner_id, save=False)

        raw = json.loads(path.read_text(encoding="utf-8"))
        badges = [BadgeAward(**item) for item in raw.get("badges", [])]
        return LearnerProfile(
            learner_id=raw.get("learner_id", learner_id),
            display_name=raw.get("display_name") or self._display_name_from_id(learner_id),
            email=raw.get("email", ""),
            home_region=raw.get("home_region", "Arkansas"),
            organization=raw.get("organization", ""),
            bio=raw.get("bio", ""),
            interests=raw.get("interests", list(DEFAULT_INTERESTS)),
            target_roles=raw.get("target_roles", []),
            civic_goals=raw.get("civic_goals", []),
            badges=badges,
            metadata=raw.get("metadata", {}),
            created_at=raw.get("created_at", utc_now_iso()),
            updated_at=raw.get("updated_at", utc_now_iso()),
        )

    def create_profile(
        self,
        learner_id: str,
        display_name: str | None = None,
        organization: str = "",
        interests: list[str] | None = None,
        target_roles: list[str] | None = None,
        civic_goals: list[str] | None = None,
        save: bool = True,
    ) -> LearnerProfile:
        profile = LearnerProfile(
            learner_id=learner_id,
            display_name=display_name or self._display_name_from_id(learner_id),
            organization=organization,
            interests=interests or list(DEFAULT_INTERESTS),
            target_roles=target_roles or [],
            civic_goals=civic_goals or [],
        )
        if save:
            self.save_profile(profile)
        return profile

    def save_profile(self, profile: LearnerProfile) -> Path:
        profile.updated_at = utc_now_iso()
        path = self.learner_profile_path(profile.learner_id)
        path.write_text(json.dumps(profile.to_dict(), indent=2), encoding="utf-8")
        return path

    def upsert_profile(self, learner_id: str, **updates: Any) -> LearnerProfile:
        profile = self.load_profile(learner_id)
        for field_name, value in updates.items():
            if hasattr(profile, field_name) and value is not None:
                setattr(profile, field_name, value)
        self.save_profile(profile)
        return profile

    # ---------------------------------------------------------
    # learner discovery and inference
    # ---------------------------------------------------------

    def discover_learner_ids(self) -> list[str]:
        analytics_ids = set(self.analytics_engine.discover_learner_ids())
        identity_ids = {
            path.stem.replace("_profile", "")
            for path in self.learners_dir.glob("*_profile.json")
        }
        all_ids = sorted(analytics_ids | identity_ids)
        return all_ids

    def award_badge_if_missing(
        self,
        profile: LearnerProfile,
        badge_slug: str,
        title: str,
        description: str,
        source: str,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        if any(b.badge_slug == badge_slug for b in profile.badges):
            return
        profile.badges.append(
            BadgeAward(
                badge_slug=badge_slug,
                title=title,
                description=description,
                awarded_at=utc_now_iso(),
                source=source,
                metadata=metadata or {},
            )
        )

    def build_identity_snapshot(self, learner_id: str) -> dict[str, Any]:
        profile = self.load_profile(learner_id)
        analytics = self.analytics_engine.rebuild_learner_summary(learner_id).to_dict()
        tracks = self.track_engine.build_track_definitions()

        active_hours = float(analytics.get("active_hours", 0.0))
        volunteer_hours = float(analytics.get("volunteer_hours", 0.0))
        completed_segments = int(analytics.get("total_completed_segments", 0))

        readiness = self._infer_readiness(active_hours, volunteer_hours, completed_segments)
        role_signals = self._infer_role_signals(profile, analytics)
        recommended_tracks = self._recommend_tracks(profile, analytics, tracks)

        if active_hours >= 1:
            self.award_badge_if_missing(
                profile,
                badge_slug="first-hour-in-system",
                title="First Hour in the System",
                description="Logged the first meaningful hour of civic learning.",
                source="engine.user_identity_engine",
                metadata={"active_hours": active_hours},
            )
        if completed_segments >= 5:
            self.award_badge_if_missing(
                profile,
                badge_slug="lesson-finisher",
                title="Lesson Finisher",
                description="Completed five or more lesson segments.",
                source="engine.user_identity_engine",
                metadata={"completed_segments": completed_segments},
            )
        if volunteer_hours >= 2:
            self.award_badge_if_missing(
                profile,
                badge_slug="community-shows-up",
                title="Community Shows Up",
                description="Recorded at least two approved volunteer hours.",
                source="engine.user_identity_engine",
                metadata={"volunteer_hours": volunteer_hours},
            )

        self.save_profile(profile)

        snapshot = {
            "generated_at": utc_now_iso(),
            "generated_by": "engine.user_identity_engine",
            "learner_id": learner_id,
            "profile": profile.to_dict(),
            "analytics_summary": analytics,
            "readiness": readiness,
            "role_signals": role_signals,
            "recommended_tracks": recommended_tracks,
            "next_actions": self._build_next_actions(readiness, role_signals, recommended_tracks),
        }

        output_path = self.exports_dir / f"{learner_id}_identity_snapshot.json"
        output_path.write_text(json.dumps(snapshot, indent=2), encoding="utf-8")
        return snapshot

    def build_platform_identity_index(self) -> dict[str, Any]:
        learner_ids = self.discover_learner_ids()
        learners = [self.build_identity_snapshot(learner_id) for learner_id in learner_ids]

        badge_counts: dict[str, int] = {}
        for learner in learners:
            for badge in learner.get("profile", {}).get("badges", []):
                badge_counts[badge["badge_slug"]] = badge_counts.get(badge["badge_slug"], 0) + 1

        payload = {
            "generated_at": utc_now_iso(),
            "generated_by": "engine.user_identity_engine",
            "learner_count": len(learners),
            "badge_counts": badge_counts,
            "learners": learners,
        }
        path = self.exports_dir / "identity_index.json"
        path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        return payload

    # ---------------------------------------------------------
    # heuristics
    # ---------------------------------------------------------

    def _display_name_from_id(self, learner_id: str) -> str:
        return learner_id.replace("_", " ").replace("-", " ").strip().title() or "Learner"

    def _infer_readiness(
        self,
        active_hours: float,
        volunteer_hours: float,
        completed_segments: int,
    ) -> dict[str, Any]:
        if active_hours < 1:
            stage = "onboarding"
            score = 15
        elif active_hours < 5:
            stage = "foundation"
            score = 35
        elif active_hours < 15:
            stage = "applied-learning"
            score = 60
        elif active_hours < 40:
            stage = "leadership-pipeline"
            score = 80
        else:
            stage = "civic-instructor"
            score = 95

        score = min(100, score + min(20, completed_segments) + int(min(10, volunteer_hours * 2)))

        return {
            "stage": stage,
            "score": score,
            "active_hours": active_hours,
            "volunteer_hours": volunteer_hours,
            "completed_segments": completed_segments,
        }

    def _infer_role_signals(self, profile: LearnerProfile, analytics: dict[str, Any]) -> list[dict[str, Any]]:
        course_rollups = analytics.get("course_rollups", {}) or {}

        signals = [
            {
                "role": "community-organizer",
                "score": 0,
                "why": [],
            },
            {
                "role": "campaign-manager",
                "score": 0,
                "why": [],
            },
            {
                "role": "narrative-strategist",
                "score": 0,
                "why": [],
            },
            {
                "role": "policy-researcher",
                "score": 0,
                "why": [],
            },
        ]
        index = {item["role"]: item for item in signals}

        interests_text = " ".join(profile.interests + profile.target_roles + profile.civic_goals).lower()
        if "organ" in interests_text or "community" in interests_text:
            index["community-organizer"]["score"] += 20
            index["community-organizer"]["why"].append("Profile interests mention organizing or community work.")
        if "campaign" in interests_text or "field" in interests_text:
            index["campaign-manager"]["score"] += 20
            index["campaign-manager"]["why"].append("Profile interests mention campaign or field work.")
        if "media" in interests_text or "message" in interests_text or "story" in interests_text:
            index["narrative-strategist"]["score"] += 20
            index["narrative-strategist"]["why"].append("Profile interests mention media, message, or story.")
        if "policy" in interests_text or "research" in interests_text or "law" in interests_text:
            index["policy-researcher"]["score"] += 20
            index["policy-researcher"]["why"].append("Profile interests mention policy, law, or research.")

        for course_slug, rollup in course_rollups.items():
            slug = str(course_slug).lower()
            active_hours = float(rollup.get("active_hours", 0.0))
            if any(term in slug for term in ["coalition", "shared_pain", "organizer", "ecosystem"]):
                index["community-organizer"]["score"] += int(active_hours * 5) + 5
                index["community-organizer"]["why"].append(f"Engagement in {course_slug} supports organizing readiness.")
            if any(term in slug for term in ["strategy", "campaign", "voting_systems", "direct_democracy"]):
                index["campaign-manager"]["score"] += int(active_hours * 5) + 5
                index["campaign-manager"]["why"].append(f"Engagement in {course_slug} supports campaign systems thinking.")
            if any(term in slug for term in ["messaging", "narrative", "shared_pain"]):
                index["narrative-strategist"]["score"] += int(active_hours * 5) + 5
                index["narrative-strategist"]["why"].append(f"Engagement in {course_slug} supports narrative strategy.")
            if any(term in slug for term in ["history", "voting_systems", "direct_democracy"]):
                index["policy-researcher"]["score"] += int(active_hours * 4) + 4
                index["policy-researcher"]["why"].append(f"Engagement in {course_slug} supports civic and policy research.")

        return sorted(signals, key=lambda item: item["score"], reverse=True)

    def _recommend_tracks(
        self,
        profile: LearnerProfile,
        analytics: dict[str, Any],
        tracks: list[Any],
    ) -> list[dict[str, Any]]:
        completed_course_slugs = {
            slug
            for slug, rollup in (analytics.get("course_rollups", {}) or {}).items()
            if int(rollup.get("completed_segments", 0)) > 0 or float(rollup.get("active_hours", 0)) >= 1
        }
        top_role = None
        role_signals = self._infer_role_signals(profile, analytics)
        if role_signals:
            top_role = role_signals[0]["role"]

        recommendations: list[dict[str, Any]] = []
        for track in tracks:
            payload = track.to_dict()
            title = str(payload.get("title", ""))
            slug = str(payload.get("slug", ""))
            focus_tags = [str(tag).lower() for tag in payload.get("focus_tags", [])]
            track_course_slugs = {
                ref["course_slug"]
                for milestone in payload.get("milestones", [])
                for ref in milestone.get("course_refs", [])
            }
            overlap = len(track_course_slugs & completed_course_slugs)

            score = 10 + overlap * 8
            reasons: list[str] = []

            if payload.get("metadata", {}).get("recommended_entry"):
                score += 12
                reasons.append("This is the recommended entry pathway for the platform.")

            if top_role == "community-organizer" and ("organizing" in focus_tags or "leadership" in focus_tags):
                score += 15
                reasons.append("Matches the learner's strongest organizing signal.")
            if top_role == "campaign-manager" and any(tag in focus_tags for tag in ["campaigns", "strategy"]):
                score += 15
                reasons.append("Matches the learner's strongest campaign systems signal.")
            if top_role == "narrative-strategist" and any(tag in focus_tags for tag in ["narrative", "media", "messaging"]):
                score += 15
                reasons.append("Matches the learner's strongest storytelling signal.")
            if top_role == "policy-researcher" and any(tag in focus_tags for tag in ["history", "civics", "policy"]):
                score += 15
                reasons.append("Matches the learner's strongest policy research signal.")

            if overlap > 0:
                reasons.append(f"Learner already has momentum in {overlap} course(s) in this pathway.")
            else:
                reasons.append("This pathway would open a new area of civic development.")

            recommendations.append(
                {
                    "track_slug": slug,
                    "title": title,
                    "score": score,
                    "estimated_hours": payload.get("estimated_hours", 0),
                    "focus_tags": payload.get("focus_tags", []),
                    "reasons": reasons,
                }
            )

        return sorted(recommendations, key=lambda item: item["score"], reverse=True)[:5]

    def _build_next_actions(
        self,
        readiness: dict[str, Any],
        role_signals: list[dict[str, Any]],
        recommended_tracks: list[dict[str, Any]],
    ) -> list[str]:
        actions: list[str] = []
        stage = readiness.get("stage")
        if stage == "onboarding":
            actions.append("Complete an initial foundations lesson and record your first hour of active learning.")
            actions.append("Choose one target civic role so the system can personalize your track recommendations.")
        elif stage == "foundation":
            actions.append("Finish a second course cluster and start building consistency across weeks, not just one session.")
            actions.append("Log at least one real-world volunteer action to bridge study with public work.")
        elif stage == "applied-learning":
            actions.append("Commit to a track and begin milestone-based progress toward leadership readiness.")
            actions.append("Translate learning into action by joining a campaign, community meeting, or organizing effort.")
        else:
            actions.append("Document your specialty role and begin mentoring others through shared practice.")
            actions.append("Use the analytics and mentor layers to identify weak spots in your civic stack.")

        if role_signals:
            actions.append(f"Top role signal: {role_signals[0]['role']}. Build your next steps around that lane.")
        if recommended_tracks:
            actions.append(f"Top recommended track: {recommended_tracks[0]['title']}.")
        return actions[:5]


if __name__ == "__main__":
    engine = UserIdentityEngine()
    payload = engine.build_platform_identity_index()
    print(json.dumps({
        "generated_at": payload["generated_at"],
        "learner_count": payload["learner_count"],
        "badge_counts": payload["badge_counts"],
    }, indent=2))
