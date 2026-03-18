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


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass
class SegmentProgress:
    course_slug: str
    chapter_slug: str
    segment_name: str
    completed: bool = False
    active_seconds: int = 0
    idle_seconds: int = 0
    session_count: int = 0
    first_started_at: str | None = None
    last_activity_at: str | None = None
    completed_at: str | None = None

    def key(self) -> str:
        return f"{self.course_slug}/{self.chapter_slug}/{self.segment_name}"

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class LearningSession:
    session_id: str
    learner_id: str
    course_slug: str
    chapter_slug: str
    segment_name: str
    started_at: str
    last_heartbeat_at: str
    status: str = "active"
    active_seconds: int = 0
    idle_seconds: int = 0
    pause_count: int = 0
    completed: bool = False
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class LearnerProgressState:
    learner_id: str
    total_active_seconds: int = 0
    total_idle_seconds: int = 0
    total_completed_segments: int = 0
    total_sessions: int = 0
    segments: dict[str, SegmentProgress] = field(default_factory=dict)
    sessions: list[LearningSession] = field(default_factory=list)
    updated_at: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "learner_id": self.learner_id,
            "total_active_seconds": self.total_active_seconds,
            "total_idle_seconds": self.total_idle_seconds,
            "total_completed_segments": self.total_completed_segments,
            "total_sessions": self.total_sessions,
            "updated_at": self.updated_at,
            "segments": {k: v.to_dict() for k, v in self.segments.items()},
            "sessions": [s.to_dict() for s in self.sessions],
        }


class ProgressEngine:
    """
    File-backed learning progress engine.

    This is deliberately filesystem-first until a database layer exists.
    It provides the canonical model for:
      - active learning seconds
      - idle seconds
      - session lifecycle
      - completion state
      - future database migration
    """

    def __init__(self, root: str | Path | None = None) -> None:
        self.kernel = create_kernel(root)
        self.root = self.kernel.root
        self.runtime_dir = self.kernel.ensure_export_dir("learning_runtime")

    def learner_state_path(self, learner_id: str) -> Path:
        safe = learner_id.replace("/", "_").replace("\\", "_").strip() or "anonymous"
        return self.runtime_dir / f"{safe}_progress_state.json"

    def load_state(self, learner_id: str = "demo_learner") -> LearnerProgressState:
        path = self.learner_state_path(learner_id)
        if not path.exists():
            return LearnerProgressState(learner_id=learner_id, updated_at=utc_now_iso())

        payload = json.loads(path.read_text(encoding="utf-8"))
        state = LearnerProgressState(
            learner_id=payload.get("learner_id", learner_id),
            total_active_seconds=payload.get("total_active_seconds", 0),
            total_idle_seconds=payload.get("total_idle_seconds", 0),
            total_completed_segments=payload.get("total_completed_segments", 0),
            total_sessions=payload.get("total_sessions", 0),
            updated_at=payload.get("updated_at"),
        )

        for key, value in payload.get("segments", {}).items():
            state.segments[key] = SegmentProgress(**value)

        for raw in payload.get("sessions", []):
            state.sessions.append(LearningSession(**raw))

        return state

    def save_state(self, state: LearnerProgressState) -> Path:
        state.updated_at = utc_now_iso()
        path = self.learner_state_path(state.learner_id)
        path.write_text(json.dumps(state.to_dict(), indent=2), encoding="utf-8")
        return path

    def ensure_segment(self, state: LearnerProgressState, course_slug: str, chapter_slug: str, segment_name: str) -> SegmentProgress:
        key = f"{course_slug}/{chapter_slug}/{segment_name}"
        if key not in state.segments:
            state.segments[key] = SegmentProgress(
                course_slug=course_slug,
                chapter_slug=chapter_slug,
                segment_name=segment_name,
            )
        return state.segments[key]

    def start_session(
        self,
        learner_id: str,
        course_slug: str,
        chapter_slug: str,
        segment_name: str,
        metadata: dict[str, Any] | None = None,
    ) -> tuple[LearnerProgressState, LearningSession]:
        state = self.load_state(learner_id)
        session = LearningSession(
            session_id=str(uuid.uuid4()),
            learner_id=learner_id,
            course_slug=course_slug,
            chapter_slug=chapter_slug,
            segment_name=segment_name,
            started_at=utc_now_iso(),
            last_heartbeat_at=utc_now_iso(),
            metadata=metadata or {},
        )
        state.sessions.append(session)
        state.total_sessions += 1

        segment = self.ensure_segment(state, course_slug, chapter_slug, segment_name)
        segment.session_count += 1
        segment.last_activity_at = utc_now_iso()
        if segment.first_started_at is None:
            segment.first_started_at = utc_now_iso()

        self.save_state(state)
        return state, session

    def apply_runtime_update(
        self,
        learner_id: str,
        course_slug: str,
        chapter_slug: str,
        segment_name: str,
        active_seconds: int = 0,
        idle_seconds: int = 0,
        completed: bool = False,
    ) -> LearnerProgressState:
        state = self.load_state(learner_id)
        segment = self.ensure_segment(state, course_slug, chapter_slug, segment_name)

        segment.active_seconds += max(0, int(active_seconds))
        segment.idle_seconds += max(0, int(idle_seconds))
        segment.last_activity_at = utc_now_iso()

        state.total_active_seconds += max(0, int(active_seconds))
        state.total_idle_seconds += max(0, int(idle_seconds))

        if completed and not segment.completed:
            segment.completed = True
            segment.completed_at = utc_now_iso()
            state.total_completed_segments += 1

        self.save_state(state)
        return state

    def build_runtime_snapshot(self, learner_id: str = "demo_learner") -> dict[str, Any]:
        state = self.load_state(learner_id)
        return {
            "learner_id": state.learner_id,
            "database_connected": False,
            "persistence": "filesystem",
            "generated_at": utc_now_iso(),
            "summary": {
                "total_active_seconds": state.total_active_seconds,
                "total_idle_seconds": state.total_idle_seconds,
                "total_completed_segments": state.total_completed_segments,
                "total_sessions": state.total_sessions,
            },
            "segments": [segment.to_dict() for segment in state.segments.values()],
            "sessions": [session.to_dict() for session in state.sessions[-25:]],
        }

    def export_runtime_snapshot(self, learner_id: str = "demo_learner") -> Path:
        payload = self.build_runtime_snapshot(learner_id)
        output_path = self.runtime_dir / "learning_runtime_snapshot.json"
        output_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        return output_path
