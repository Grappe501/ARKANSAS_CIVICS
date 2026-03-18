from __future__ import annotations

from dataclasses import dataclass, asdict, field
from pathlib import Path
from typing import Any
from datetime import datetime, timezone
import json
import uuid
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from engine.platform_kernel import create_kernel  # noqa: E402


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def safe_slug(value: str) -> str:
    return (
        str(value)
        .strip()
        .lower()
        .replace(" ", "_")
        .replace("/", "_")
        .replace("\\", "_")
        .replace("-", "_")
    )


@dataclass
class CivicActionLog:
    log_id: str
    learner_id: str
    action_type: str
    title: str
    description: str = ""
    organization: str = ""
    occurred_at: str = ""
    hours: float = 0.0
    evidence: list[str] = field(default_factory=list)
    approved: bool = False
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class CourseProgressRecord:
    course_slug: str
    started_at: str | None = None
    completed_at: str | None = None
    completion_percent: float = 0.0
    completed_segments: int = 0
    total_segments: int = 0
    learning_hours: float = 0.0
    status: str = "not_started"

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class LearnerProgressProfile:
    learner_id: str
    created_at: str
    updated_at: str
    enrolled_tracks: list[str] = field(default_factory=list)
    completed_tracks: list[str] = field(default_factory=list)
    learning_hours_total: float = 0.0
    civic_action_hours_total: float = 0.0
    volunteer_hours_total: float = 0.0
    approved_action_hours_total: float = 0.0
    courses: dict[str, CourseProgressRecord] = field(default_factory=dict)
    earned_badges: list[str] = field(default_factory=list)
    earned_certifications: list[str] = field(default_factory=list)
    leadership_tier: str = "tier_0"
    civic_actions: list[CivicActionLog] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "learner_id": self.learner_id,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "enrolled_tracks": self.enrolled_tracks,
            "completed_tracks": self.completed_tracks,
            "learning_hours_total": self.learning_hours_total,
            "civic_action_hours_total": self.civic_action_hours_total,
            "volunteer_hours_total": self.volunteer_hours_total,
            "approved_action_hours_total": self.approved_action_hours_total,
            "courses": {k: v.to_dict() for k, v in self.courses.items()},
            "earned_badges": self.earned_badges,
            "earned_certifications": self.earned_certifications,
            "leadership_tier": self.leadership_tier,
            "civic_actions": [a.to_dict() for a in self.civic_actions],
            "metadata": self.metadata,
        }


class ProgressRegistry:
    """
    Filesystem-first learner progress registry for Arkansas Civics.

    This phase introduces:
    - course completion rollups
    - civic action tracking
    - badge/certification attachment points
    - learner readiness summaries
    """

    def __init__(self, root: str | Path | None = None) -> None:
        self.kernel = create_kernel(root)
        self.root = self.kernel.root

        self.progress_registry_dir = self.kernel.data_dir / "registry"
        self.progress_profiles_dir = self.progress_registry_dir / "learners"
        self.progress_exports_dir = self.kernel.ensure_export_dir("progress_registry")

        self.progress_registry_dir.mkdir(parents=True, exist_ok=True)
        self.progress_profiles_dir.mkdir(parents=True, exist_ok=True)
        self.progress_exports_dir.mkdir(parents=True, exist_ok=True)

    def profile_path(self, learner_id: str) -> Path:
        return self.progress_profiles_dir / f"{safe_slug(learner_id)}_registry.json"

    def load_profile(self, learner_id: str) -> LearnerProgressProfile:
        path = self.profile_path(learner_id)
        if not path.exists():
            now = utc_now_iso()
            profile = LearnerProgressProfile(
                learner_id=learner_id,
                created_at=now,
                updated_at=now,
            )
            self.save_profile(profile)
            return profile

        raw = json.loads(path.read_text(encoding="utf-8"))
        courses = {
            k: CourseProgressRecord(**v)
            for k, v in raw.get("courses", {}).items()
        }
        civic_actions = [CivicActionLog(**a) for a in raw.get("civic_actions", [])]

        return LearnerProgressProfile(
            learner_id=raw["learner_id"],
            created_at=raw.get("created_at", utc_now_iso()),
            updated_at=raw.get("updated_at", utc_now_iso()),
            enrolled_tracks=raw.get("enrolled_tracks", []),
            completed_tracks=raw.get("completed_tracks", []),
            learning_hours_total=float(raw.get("learning_hours_total", 0.0)),
            civic_action_hours_total=float(raw.get("civic_action_hours_total", 0.0)),
            volunteer_hours_total=float(raw.get("volunteer_hours_total", 0.0)),
            approved_action_hours_total=float(raw.get("approved_action_hours_total", 0.0)),
            courses=courses,
            earned_badges=raw.get("earned_badges", []),
            earned_certifications=raw.get("earned_certifications", []),
            leadership_tier=raw.get("leadership_tier", "tier_0"),
            civic_actions=civic_actions,
            metadata=raw.get("metadata", {}),
        )

    def save_profile(self, profile: LearnerProgressProfile) -> Path:
        profile.updated_at = utc_now_iso()
        path = self.profile_path(profile.learner_id)
        path.write_text(json.dumps(profile.to_dict(), indent=2), encoding="utf-8")
        return path

    def ensure_course(self, profile: LearnerProgressProfile, course_slug: str) -> CourseProgressRecord:
        course_slug = safe_slug(course_slug)
        if course_slug not in profile.courses:
            profile.courses[course_slug] = CourseProgressRecord(course_slug=course_slug)
        return profile.courses[course_slug]

    def enroll_track(self, learner_id: str, track_slug: str) -> LearnerProgressProfile:
        profile = self.load_profile(learner_id)
        track_slug = safe_slug(track_slug)
        if track_slug not in profile.enrolled_tracks:
            profile.enrolled_tracks.append(track_slug)
        return self._finalize(profile)

    def mark_track_completed(self, learner_id: str, track_slug: str) -> LearnerProgressProfile:
        profile = self.load_profile(learner_id)
        track_slug = safe_slug(track_slug)
        if track_slug not in profile.completed_tracks:
            profile.completed_tracks.append(track_slug)
        if track_slug not in profile.enrolled_tracks:
            profile.enrolled_tracks.append(track_slug)
        return self._finalize(profile)

    def record_course_progress(
        self,
        learner_id: str,
        course_slug: str,
        completed_segments: int = 0,
        total_segments: int = 0,
        learning_hours: float = 0.0,
        completed: bool = False,
    ) -> LearnerProgressProfile:
        profile = self.load_profile(learner_id)
        course = self.ensure_course(profile, course_slug)

        if course.started_at is None:
            course.started_at = utc_now_iso()

        course.completed_segments = max(course.completed_segments, int(completed_segments))
        course.total_segments = max(course.total_segments, int(total_segments))
        course.learning_hours = max(course.learning_hours, round(float(learning_hours), 2))

        if course.total_segments > 0:
            course.completion_percent = round(
                min(100.0, (course.completed_segments / course.total_segments) * 100.0),
                2,
            )

        if completed or (course.total_segments > 0 and course.completed_segments >= course.total_segments):
            course.completed_at = course.completed_at or utc_now_iso()
            course.status = "completed"
            course.completion_percent = 100.0
        elif course.completed_segments > 0:
            course.status = "in_progress"
        else:
            course.status = "not_started"

        return self._finalize(profile)

    def add_badge(self, learner_id: str, badge_slug: str) -> LearnerProgressProfile:
        profile = self.load_profile(learner_id)
        badge_slug = safe_slug(badge_slug)
        if badge_slug not in profile.earned_badges:
            profile.earned_badges.append(badge_slug)
        return self._finalize(profile)

    def add_certification(self, learner_id: str, certification_slug: str) -> LearnerProgressProfile:
        profile = self.load_profile(learner_id)
        certification_slug = safe_slug(certification_slug)
        if certification_slug not in profile.earned_certifications:
            profile.earned_certifications.append(certification_slug)
        return self._finalize(profile)

    def set_leadership_tier(self, learner_id: str, tier_slug: str) -> LearnerProgressProfile:
        profile = self.load_profile(learner_id)
        profile.leadership_tier = safe_slug(tier_slug)
        return self._finalize(profile)

    def log_civic_action(
        self,
        learner_id: str,
        action_type: str,
        title: str,
        description: str = "",
        organization: str = "",
        hours: float = 0.0,
        approved: bool = False,
        evidence: list[str] | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> LearnerProgressProfile:
        profile = self.load_profile(learner_id)
        action = CivicActionLog(
            log_id=str(uuid.uuid4()),
            learner_id=learner_id,
            action_type=safe_slug(action_type),
            title=title,
            description=description,
            organization=organization,
            occurred_at=utc_now_iso(),
            hours=round(max(0.0, float(hours)), 2),
            approved=approved,
            evidence=evidence or [],
            metadata=metadata or {},
        )
        profile.civic_actions.append(action)
        return self._finalize(profile)

    def approve_civic_action(self, learner_id: str, log_id: str) -> LearnerProgressProfile:
        profile = self.load_profile(learner_id)
        for action in profile.civic_actions:
            if action.log_id == log_id:
                action.approved = True
                break
        return self._finalize(profile)

    def _finalize(self, profile: LearnerProgressProfile) -> LearnerProgressProfile:
        profile.learning_hours_total = round(
            sum(course.learning_hours for course in profile.courses.values()),
            2,
        )
        profile.civic_action_hours_total = round(
            sum(action.hours for action in profile.civic_actions),
            2,
        )
        profile.approved_action_hours_total = round(
            sum(action.hours for action in profile.civic_actions if action.approved),
            2,
        )
        profile.volunteer_hours_total = round(
            sum(action.hours for action in profile.civic_actions if action.action_type == "volunteer"),
            2,
        )
        self.save_profile(profile)
        return profile

    def learner_index(self) -> list[str]:
        return sorted(path.stem.replace("_registry", "") for path in self.progress_profiles_dir.glob("*_registry.json"))

    def export_registry_index(self) -> list[Path]:
        learners = []
        summary = {
            "learner_count": 0,
            "learning_hours_total": 0.0,
            "civic_action_hours_total": 0.0,
            "approved_action_hours_total": 0.0,
            "badge_count_total": 0,
            "certification_count_total": 0,
            "completed_course_count_total": 0,
        }

        for learner_slug in self.learner_index():
            profile = self.load_profile(learner_slug)
            learner_payload = profile.to_dict()
            learner_payload["completed_course_count"] = sum(
                1 for course in profile.courses.values() if course.status == "completed"
            )
            learners.append(learner_payload)

            summary["learner_count"] += 1
            summary["learning_hours_total"] += profile.learning_hours_total
            summary["civic_action_hours_total"] += profile.civic_action_hours_total
            summary["approved_action_hours_total"] += profile.approved_action_hours_total
            summary["badge_count_total"] += len(profile.earned_badges)
            summary["certification_count_total"] += len(profile.earned_certifications)
            summary["completed_course_count_total"] += learner_payload["completed_course_count"]

        summary["learning_hours_total"] = round(summary["learning_hours_total"], 2)
        summary["civic_action_hours_total"] = round(summary["civic_action_hours_total"], 2)
        summary["approved_action_hours_total"] = round(summary["approved_action_hours_total"], 2)

        registry_index = {
            "generated_at": utc_now_iso(),
            "engine": "progress_registry",
            "database_connected": False,
            "summary": summary,
            "learners": learners,
        }

        json_path = self.progress_exports_dir / "progress_registry_index.json"
        md_path = self.progress_exports_dir / "progress_registry_report.md"

        json_path.write_text(json.dumps(registry_index, indent=2), encoding="utf-8")
        md_path.write_text(self.render_markdown_report(registry_index), encoding="utf-8")
        return [json_path, md_path]

    def render_markdown_report(self, registry_index: dict[str, Any]) -> str:
        summary = registry_index["summary"]
        lines = [
            "# Arkansas Civics Progress Registry Report",
            "",
            f"- Generated at: `{registry_index['generated_at']}`",
            f"- Learners: **{summary['learner_count']}**",
            f"- Learning hours: **{summary['learning_hours_total']}**",
            f"- Civic action hours: **{summary['civic_action_hours_total']}**",
            f"- Approved action hours: **{summary['approved_action_hours_total']}**",
            f"- Total badges: **{summary['badge_count_total']}**",
            f"- Total certifications: **{summary['certification_count_total']}**",
            f"- Completed courses: **{summary['completed_course_count_total']}**",
            "",
            "## Learner Summaries",
            "",
        ]

        if not registry_index["learners"]:
            lines.append("_No learner progress profiles found yet._")
            lines.append("")
            return "\n".join(lines)

        for learner in registry_index["learners"]:
            lines.extend([
                f"### {learner['learner_id']}",
                f"- Leadership tier: {learner['leadership_tier']}",
                f"- Learning hours: {learner['learning_hours_total']}",
                f"- Civic action hours: {learner['civic_action_hours_total']}",
                f"- Badges: {len(learner['earned_badges'])}",
                f"- Certifications: {len(learner['earned_certifications'])}",
                "",
            ])
        return "\n".join(lines)
