from __future__ import annotations

from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Any
from datetime import datetime, timezone
import json
import sys
import uuid

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from engine.platform_kernel import create_kernel  # noqa: E402
from engine.progress_engine import ProgressEngine  # noqa: E402


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def seconds_to_hours(seconds: int) -> float:
    return round(max(0, int(seconds)) / 3600, 2)


def safe_int(value: Any, default: int = 0) -> int:
    try:
        if value is None:
            return default
        return int(value)
    except (TypeError, ValueError):
        return default


def safe_bool(value: Any) -> bool:
    return bool(value)


def getattr_or_key(obj: Any, name: str, default: Any = None) -> Any:
    if isinstance(obj, dict):
        return obj.get(name, default)
    return getattr(obj, name, default)


@dataclass
class VolunteerLog:
    log_id: str
    learner_id: str
    title: str
    description: str = ""
    organization: str = ""
    occurred_at: str = ""
    duration_seconds: int = 0
    approved: bool = False
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class LearnerAnalyticsSummary:
    learner_id: str
    total_active_seconds: int = 0
    total_idle_seconds: int = 0
    total_volunteer_seconds: int = 0
    total_completed_segments: int = 0
    total_sessions: int = 0
    last_activity_at: str | None = None
    course_rollups: dict[str, dict[str, Any]] = field(default_factory=dict)
    chapter_rollups: dict[str, dict[str, Any]] = field(default_factory=dict)
    volunteer_logs: list[VolunteerLog] = field(default_factory=list)
    updated_at: str | None = None

    @property
    def active_hours(self) -> float:
        return seconds_to_hours(self.total_active_seconds)

    @property
    def idle_hours(self) -> float:
        return seconds_to_hours(self.total_idle_seconds)

    @property
    def volunteer_hours(self) -> float:
        return seconds_to_hours(self.total_volunteer_seconds)

    def to_dict(self) -> dict[str, Any]:
        return {
            "learner_id": self.learner_id,
            "total_active_seconds": self.total_active_seconds,
            "total_idle_seconds": self.total_idle_seconds,
            "total_volunteer_seconds": self.total_volunteer_seconds,
            "active_hours": self.active_hours,
            "idle_hours": self.idle_hours,
            "volunteer_hours": self.volunteer_hours,
            "total_completed_segments": self.total_completed_segments,
            "total_sessions": self.total_sessions,
            "last_activity_at": self.last_activity_at,
            "course_rollups": self.course_rollups,
            "chapter_rollups": self.chapter_rollups,
            "volunteer_logs": [log.to_dict() for log in self.volunteer_logs],
            "updated_at": self.updated_at,
        }


class LearningAnalyticsEngine:
    """
    Stand Up Arkansas Learning Analytics Engine

    Purpose:
    - turn runtime/progress activity into reporting-friendly analytics
    - preserve a filesystem-first architecture
    - support active learning, idle time, volunteer hours, and admin summaries
    - generate future-ready outputs for dashboards and eventual database migration
    """

    def __init__(self, root: str | Path | None = None) -> None:
        self.kernel = create_kernel(root)
        self.root = self.kernel.root
        self.progress_engine = ProgressEngine(root)

        self.analytics_dir = self.kernel.data_dir / "analytics"
        self.learner_dir = self.analytics_dir / "learners"
        self.admin_dir = self.analytics_dir / "admin"

        self.analytics_dir.mkdir(parents=True, exist_ok=True)
        self.learner_dir.mkdir(parents=True, exist_ok=True)
        self.admin_dir.mkdir(parents=True, exist_ok=True)

    # ---------------------------------------------------------
    # paths
    # ---------------------------------------------------------

    def learner_summary_path(self, learner_id: str) -> Path:
        safe = learner_id.replace("/", "_").replace("\\", "_")
        return self.learner_dir / f"{safe}_analytics.json"

    def admin_snapshot_path(self) -> Path:
        return self.admin_dir / "learning_admin_snapshot.json"

    def progress_dir(self) -> Path:
        return self.kernel.data_dir / "progress"

    # ---------------------------------------------------------
    # loading / saving
    # ---------------------------------------------------------

    def load_learner_summary(self, learner_id: str) -> LearnerAnalyticsSummary:
        path = self.learner_summary_path(learner_id)
        if not path.exists():
            return LearnerAnalyticsSummary(
                learner_id=learner_id,
                updated_at=utc_now_iso(),
            )

        raw = json.loads(path.read_text(encoding="utf-8"))
        logs = [VolunteerLog(**item) for item in raw.get("volunteer_logs", [])]

        return LearnerAnalyticsSummary(
            learner_id=raw["learner_id"],
            total_active_seconds=safe_int(raw.get("total_active_seconds", 0)),
            total_idle_seconds=safe_int(raw.get("total_idle_seconds", 0)),
            total_volunteer_seconds=safe_int(raw.get("total_volunteer_seconds", 0)),
            total_completed_segments=safe_int(raw.get("total_completed_segments", 0)),
            total_sessions=safe_int(raw.get("total_sessions", 0)),
            last_activity_at=raw.get("last_activity_at"),
            course_rollups=raw.get("course_rollups", {}),
            chapter_rollups=raw.get("chapter_rollups", {}),
            volunteer_logs=logs,
            updated_at=raw.get("updated_at"),
        )

    def save_learner_summary(self, summary: LearnerAnalyticsSummary) -> Path:
        summary.updated_at = utc_now_iso()
        path = self.learner_summary_path(summary.learner_id)
        path.write_text(json.dumps(summary.to_dict(), indent=2), encoding="utf-8")
        return path

    # ---------------------------------------------------------
    # aggregation
    # ---------------------------------------------------------

    def rebuild_learner_summary(self, learner_id: str) -> LearnerAnalyticsSummary:
        state = self.progress_engine.load_state(learner_id)
        existing = self.load_learner_summary(learner_id)

        summary = LearnerAnalyticsSummary(
            learner_id=learner_id,
            total_active_seconds=safe_int(getattr_or_key(state, "total_active_seconds", 0)),
            total_idle_seconds=safe_int(getattr_or_key(state, "total_idle_seconds", 0)),
            total_volunteer_seconds=sum(
                log.duration_seconds for log in existing.volunteer_logs if log.approved
            ),
            total_completed_segments=safe_int(getattr_or_key(state, "total_completed_segments", 0)),
            total_sessions=safe_int(getattr_or_key(state, "total_sessions", 0)),
            last_activity_at=getattr_or_key(state, "updated_at", utc_now_iso()),
            volunteer_logs=existing.volunteer_logs,
        )

        segments = getattr_or_key(state, "segments", {}) or {}

        for _, segment in segments.items():
            course_slug = str(getattr_or_key(segment, "course_slug", "unknown_course"))
            chapter_slug = str(getattr_or_key(segment, "chapter_slug", "unknown_chapter"))
            chapter_key = f"{course_slug}/{chapter_slug}"

            if course_slug not in summary.course_rollups:
                summary.course_rollups[course_slug] = {
                    "course_slug": course_slug,
                    "active_seconds": 0,
                    "idle_seconds": 0,
                    "completed_segments": 0,
                    "session_count": 0,
                    "active_hours": 0.0,
                    "idle_hours": 0.0,
                }

            if chapter_key not in summary.chapter_rollups:
                summary.chapter_rollups[chapter_key] = {
                    "course_slug": course_slug,
                    "chapter_slug": chapter_slug,
                    "chapter_key": chapter_key,
                    "active_seconds": 0,
                    "idle_seconds": 0,
                    "completed_segments": 0,
                    "session_count": 0,
                    "active_hours": 0.0,
                    "idle_hours": 0.0,
                }

            active_seconds = safe_int(getattr_or_key(segment, "active_seconds", 0))
            idle_seconds = safe_int(getattr_or_key(segment, "idle_seconds", 0))
            session_count = safe_int(getattr_or_key(segment, "session_count", 0))
            completed = safe_bool(getattr_or_key(segment, "completed", False))

            course_rollup = summary.course_rollups[course_slug]
            chapter_rollup = summary.chapter_rollups[chapter_key]

            course_rollup["active_seconds"] += active_seconds
            course_rollup["idle_seconds"] += idle_seconds
            course_rollup["session_count"] += session_count
            if completed:
                course_rollup["completed_segments"] += 1

            chapter_rollup["active_seconds"] += active_seconds
            chapter_rollup["idle_seconds"] += idle_seconds
            chapter_rollup["session_count"] += session_count
            if completed:
                chapter_rollup["completed_segments"] += 1

        for rollup in summary.course_rollups.values():
            rollup["active_hours"] = seconds_to_hours(rollup["active_seconds"])
            rollup["idle_hours"] = seconds_to_hours(rollup["idle_seconds"])

        for rollup in summary.chapter_rollups.values():
            rollup["active_hours"] = seconds_to_hours(rollup["active_seconds"])
            rollup["idle_hours"] = seconds_to_hours(rollup["idle_seconds"])

        self.save_learner_summary(summary)
        return summary

    # ---------------------------------------------------------
    # runtime integration
    # ---------------------------------------------------------

    def record_learning_activity(
        self,
        learner_id: str,
        course_slug: str,
        chapter_slug: str,
        segment_name: str,
        active_seconds: int = 0,
        idle_seconds: int = 0,
        completed: bool = False,
    ) -> LearnerAnalyticsSummary:
        self.progress_engine.apply_runtime_update(
            learner_id=learner_id,
            course_slug=course_slug,
            chapter_slug=chapter_slug,
            segment_name=segment_name,
            active_seconds=active_seconds,
            idle_seconds=idle_seconds,
            completed=completed,
        )
        return self.rebuild_learner_summary(learner_id)

    # ---------------------------------------------------------
    # volunteer hour logging
    # ---------------------------------------------------------

    def log_volunteer_hours(
        self,
        learner_id: str,
        title: str,
        duration_seconds: int,
        description: str = "",
        organization: str = "",
        occurred_at: str | None = None,
        approved: bool = False,
        metadata: dict[str, Any] | None = None,
    ) -> LearnerAnalyticsSummary:
        summary = self.load_learner_summary(learner_id)

        log = VolunteerLog(
            log_id=str(uuid.uuid4()),
            learner_id=learner_id,
            title=title,
            description=description,
            organization=organization,
            occurred_at=occurred_at or utc_now_iso(),
            duration_seconds=max(0, int(duration_seconds)),
            approved=approved,
            metadata=metadata or {},
        )

        summary.volunteer_logs.append(log)
        summary.total_volunteer_seconds = sum(
            item.duration_seconds for item in summary.volunteer_logs if item.approved
        )
        self.save_learner_summary(summary)
        return self.rebuild_learner_summary(learner_id)

    def approve_volunteer_log(self, learner_id: str, log_id: str) -> LearnerAnalyticsSummary:
        summary = self.load_learner_summary(learner_id)

        for log in summary.volunteer_logs:
            if log.log_id == log_id:
                log.approved = True
                break

        summary.total_volunteer_seconds = sum(
            item.duration_seconds for item in summary.volunteer_logs if item.approved
        )
        self.save_learner_summary(summary)
        return self.rebuild_learner_summary(learner_id)

    # ---------------------------------------------------------
    # admin analytics
    # ---------------------------------------------------------

    def discover_learner_ids(self) -> list[str]:
        learner_ids: list[str] = []
        progress_dir = self.progress_dir()

        if not progress_dir.exists():
            return learner_ids

        for path in sorted(progress_dir.glob("*_progress.json")):
            learner_ids.append(path.stem.replace("_progress", ""))

        return learner_ids

    def build_admin_snapshot(self) -> dict[str, Any]:
        learner_ids = self.discover_learner_ids()

        learners: list[dict[str, Any]] = []
        course_totals: dict[str, dict[str, Any]] = {}

        total_active_seconds = 0
        total_idle_seconds = 0
        total_volunteer_seconds = 0
        total_completed_segments = 0
        total_sessions = 0

        for learner_id in learner_ids:
            summary = self.rebuild_learner_summary(learner_id)
            learners.append(summary.to_dict())

            total_active_seconds += summary.total_active_seconds
            total_idle_seconds += summary.total_idle_seconds
            total_volunteer_seconds += summary.total_volunteer_seconds
            total_completed_segments += summary.total_completed_segments
            total_sessions += summary.total_sessions

            for course_slug, rollup in summary.course_rollups.items():
                if course_slug not in course_totals:
                    course_totals[course_slug] = {
                        "course_slug": course_slug,
                        "learner_count": 0,
                        "active_seconds": 0,
                        "idle_seconds": 0,
                        "completed_segments": 0,
                        "session_count": 0,
                        "active_hours": 0.0,
                        "idle_hours": 0.0,
                    }

                course_totals[course_slug]["learner_count"] += 1
                course_totals[course_slug]["active_seconds"] += safe_int(
                    rollup.get("active_seconds", 0)
                )
                course_totals[course_slug]["idle_seconds"] += safe_int(
                    rollup.get("idle_seconds", 0)
                )
                course_totals[course_slug]["completed_segments"] += safe_int(
                    rollup.get("completed_segments", 0)
                )
                course_totals[course_slug]["session_count"] += safe_int(
                    rollup.get("session_count", 0)
                )

        for rollup in course_totals.values():
            rollup["active_hours"] = seconds_to_hours(rollup["active_seconds"])
            rollup["idle_hours"] = seconds_to_hours(rollup["idle_seconds"])

        snapshot = {
            "generated_at": utc_now_iso(),
            "generated_by": "engine.learning_analytics_engine",
            "source_of_truth": "data/progress + data/analytics",
            "database_connected": False,
            "summary": {
                "learner_count": len(learner_ids),
                "total_active_seconds": total_active_seconds,
                "total_idle_seconds": total_idle_seconds,
                "total_volunteer_seconds": total_volunteer_seconds,
                "total_completed_segments": total_completed_segments,
                "total_sessions": total_sessions,
                "total_active_hours": seconds_to_hours(total_active_seconds),
                "total_idle_hours": seconds_to_hours(total_idle_seconds),
                "total_volunteer_hours": seconds_to_hours(total_volunteer_seconds),
            },
            "course_totals": sorted(
                course_totals.values(),
                key=lambda item: item["active_seconds"],
                reverse=True,
            ),
            "learners": learners,
        }

        self.admin_snapshot_path().write_text(json.dumps(snapshot, indent=2), encoding="utf-8")
        return snapshot

    # ---------------------------------------------------------
    # exports
    # ---------------------------------------------------------

    def render_admin_markdown(self, snapshot: dict[str, Any]) -> str:
        summary = snapshot["summary"]
        lines = [
            "# Stand Up Arkansas Learning Analytics Report",
            "",
            f"- Generated at: `{snapshot['generated_at']}`",
            f"- Learners: **{summary['learner_count']}**",
            f"- Active learning hours: **{summary['total_active_hours']}**",
            f"- Idle hours: **{summary['total_idle_hours']}**",
            f"- Volunteer hours: **{summary['total_volunteer_hours']}**",
            f"- Completed segments: **{summary['total_completed_segments']}**",
            f"- Sessions: **{summary['total_sessions']}**",
            "",
            "## Course Totals",
            "",
        ]

        if not snapshot["course_totals"]:
            lines.append("_No learner analytics found yet._")
            lines.append("")
            return "\n".join(lines)

        for course in snapshot["course_totals"]:
            lines.extend(
                [
                    f"### {course['course_slug']}",
                    f"- Learners: {course['learner_count']}",
                    f"- Active hours: {course['active_hours']}",
                    f"- Idle hours: {course['idle_hours']}",
                    f"- Completed segments: {course['completed_segments']}",
                    f"- Sessions: {course['session_count']}",
                    "",
                ]
            )

        return "\n".join(lines)

    def export_admin_reports(self, output_dir: Path | None = None) -> list[Path]:
        if output_dir is None:
            output_dir = self.kernel.ensure_export_dir("analytics")

        output_dir.mkdir(parents=True, exist_ok=True)

        snapshot = self.build_admin_snapshot()

        json_path = output_dir / "learning_admin_snapshot.json"
        json_path.write_text(json.dumps(snapshot, indent=2), encoding="utf-8")

        markdown_path = output_dir / "learning_admin_report.md"
        markdown_path.write_text(self.render_admin_markdown(snapshot), encoding="utf-8")

        blueprint_path = output_dir / "learning_analytics_blueprint.json"
        blueprint = {
            "generated_at": utc_now_iso(),
            "engine": "learning_analytics_engine",
            "tracks": [
                "active_learning_seconds",
                "idle_seconds",
                "course_rollups",
                "chapter_rollups",
                "segment_completion",
                "volunteer_hours",
                "admin_dashboard_snapshots",
            ],
            "future_tables": [
                "learner_profiles",
                "analytics_sessions",
                "analytics_rollups",
                "volunteer_hour_logs",
                "admin_reports",
            ],
        }
        blueprint_path.write_text(json.dumps(blueprint, indent=2), encoding="utf-8")

        return [json_path, markdown_path, blueprint_path]


def export_learning_analytics(root: str | Path | None = None) -> list[Path]:
    engine = LearningAnalyticsEngine(root=root)
    return engine.export_admin_reports()


if __name__ == "__main__":
    engine = LearningAnalyticsEngine()
    outputs = engine.export_admin_reports()
    print("\n================================================")
    print(" Stand Up Arkansas Learning Analytics Engine")
    print("================================================\n")
    for path in outputs:
        print(path)
    print()