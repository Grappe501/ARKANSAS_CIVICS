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


@dataclass
class RuntimePolicy:
    idle_timeout_seconds: int = 180
    blackout_after_idle: bool = True
    require_interaction_resume: bool = True
    count_scroll_as_activity: bool = True
    count_navigation_as_activity: bool = True
    count_media_play_as_activity: bool = True

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class LearnerEvent:
    event_type: str
    occurred_at: str
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class LearningSession:
    learner_id: str
    started_at: str
    ended_at: str | None = None
    active_seconds: int = 0
    idle_seconds: int = 0
    paused: bool = False
    current_mode: str = "active_learning"
    events: list[LearnerEvent] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "learner_id": self.learner_id,
            "started_at": self.started_at,
            "ended_at": self.ended_at,
            "active_seconds": self.active_seconds,
            "idle_seconds": self.idle_seconds,
            "paused": self.paused,
            "current_mode": self.current_mode,
            "events": [event.to_dict() for event in self.events],
        }


class LearningRuntime:
    """
    Files-first learning runtime.

    This is the future bridge between the front-end learning clock and the eventual
    operational database layer. For now it exports runtime policy, event types, and
    sample session models into files so the product can evolve without a database.
    """

    def __init__(self, root: str | Path | None = None) -> None:
        self.kernel = create_kernel(root)
        self.root = self.kernel.root
        self.policy = RuntimePolicy()

    def now_iso(self) -> str:
        return datetime.now(timezone.utc).isoformat()

    def start_session(self, learner_id: str) -> LearningSession:
        session = LearningSession(learner_id=learner_id, started_at=self.now_iso())
        session.events.append(LearnerEvent("session_started", self.now_iso()))
        return session

    def register_event(self, session: LearningSession, event_type: str, metadata: dict[str, Any] | None = None) -> None:
        metadata = metadata or {}
        session.events.append(LearnerEvent(event_type, self.now_iso(), metadata))
        if event_type in {"scroll", "click", "keypress", "lesson_advance", "tab_focus", "video_play"}:
            if session.paused:
                session.paused = False
                session.current_mode = "active_learning"
                session.events.append(LearnerEvent("session_resumed", self.now_iso()))

    def tick_active(self, session: LearningSession, seconds: int = 1) -> None:
        if not session.paused:
            session.active_seconds += max(0, seconds)

    def tick_idle(self, session: LearningSession, seconds: int = 1) -> None:
        session.idle_seconds += max(0, seconds)
        if session.idle_seconds >= self.policy.idle_timeout_seconds:
            session.paused = True
            session.current_mode = "idle_locked" if self.policy.blackout_after_idle else "idle"

    def end_session(self, session: LearningSession) -> None:
        session.ended_at = self.now_iso()
        session.events.append(LearnerEvent("session_ended", session.ended_at))

    def get_runtime_blueprint(self) -> dict[str, Any]:
        return {
            "generated_by": "engine.learning_runtime",
            "source_of_truth": "filesystem",
            "database_connected": False,
            "policy": self.policy.to_dict(),
            "frontend_expectations": {
                "show_learning_clock": True,
                "pause_on_idle": True,
                "blackout_screen_on_idle": self.policy.blackout_after_idle,
                "resume_requires_interaction": self.policy.require_interaction_resume,
                "track_page_presence_for_analytics": True,
                "track_active_learning_for_hours": True,
            },
            "reporting_targets": [
                "education_hours",
                "volunteer_hours",
                "active_learning_time",
                "site_presence_time",
                "track_completion",
                "organization_reports",
                "donor_impact_reports",
            ],
            "future_database_tables": [
                "users",
                "learning_sessions",
                "learning_events",
                "track_progress",
                "course_progress",
                "volunteer_logs",
                "education_hour_logs",
                "ai_recommendations",
                "reports",
            ],
        }

    def export_runtime_blueprint(self, output_dir: Path | None = None) -> list[Path]:
        if output_dir is None:
            output_dir = self.kernel.ensure_export_dir("tracks")

        outputs: list[Path] = []

        blueprint_path = output_dir / "learning_runtime_blueprint.json"
        blueprint_path.write_text(json.dumps(self.get_runtime_blueprint(), indent=2), encoding="utf-8")
        outputs.append(blueprint_path)

        sample = self.start_session("demo_learner")
        self.register_event(sample, "lesson_advance", {"course_slug": "course_01_civic_awakening"})
        self.tick_active(sample, 420)
        self.tick_idle(sample, 200)
        self.register_event(sample, "scroll", {"screen": "lesson_view"})
        self.tick_active(sample, 240)
        self.end_session(sample)

        sample_path = output_dir / "learning_runtime_sample_session.json"
        sample_path.write_text(json.dumps(sample.to_dict(), indent=2), encoding="utf-8")
        outputs.append(sample_path)

        markdown_path = output_dir / "learning_runtime_blueprint.md"
        markdown_path.write_text(self.render_runtime_markdown(), encoding="utf-8")
        outputs.append(markdown_path)

        return outputs

    def render_runtime_markdown(self) -> str:
        blueprint = self.get_runtime_blueprint()
        lines = [
            "# Stand Up Arkansas Learning Runtime Blueprint",
            "",
            "This file describes the active-learning runtime model for the future public platform.",
            "",
            "## Policy",
            "",
        ]
        for key, value in blueprint["policy"].items():
            lines.append(f"- **{key}**: {value}")
        lines.extend([
            "",
            "## Reporting Targets",
            "",
        ])
        for item in blueprint["reporting_targets"]:
            lines.append(f"- {item}")
        lines.extend([
            "",
            "## Future Database Tables",
            "",
        ])
        for item in blueprint["future_database_tables"]:
            lines.append(f"- {item}")
        lines.append("")
        return "\n".join(lines)


def export_learning_runtime(root: str | Path | None = None) -> list[Path]:
    runtime = LearningRuntime(root=root)
    return runtime.export_runtime_blueprint()


if __name__ == "__main__":
    runtime = LearningRuntime()
    outputs = runtime.export_runtime_blueprint()
    print("\n================================================")
    print(" Arkansas Civics Learning Runtime")
    print("================================================\n")
    for path in outputs:
        print(path)
    print()
