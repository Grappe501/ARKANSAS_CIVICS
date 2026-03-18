from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class EngineContract:
    name: str
    version: str
    responsibilities: list[str]
    required_paths: list[str] = field(default_factory=list)
    outputs: list[str] = field(default_factory=list)
    database_ready: bool = False
    notes: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "version": self.version,
            "responsibilities": self.responsibilities,
            "required_paths": self.required_paths,
            "outputs": self.outputs,
            "database_ready": self.database_ready,
            "notes": self.notes,
        }


def get_core_engine_contracts() -> list[EngineContract]:
    return [
        EngineContract(
            name="platform_kernel",
            version="1.1.0",
            responsibilities=[
                "canonical project paths",
                "content discovery",
                "system validation",
                "environment readiness",
            ],
            required_paths=["content/courses", "scripts", "exports", "apps/editor-dashboard"],
            outputs=["exports/system_map/platform_kernel_snapshot.json", "apps/editor-dashboard/content-manifest.json"],
            database_ready=False,
        ),
        EngineContract(
            name="course_engine",
            version="1.0.0",
            responsibilities=["course normalization", "course export preparation"],
            required_paths=["content/courses"],
            outputs=["exports/course_engine"],
        ),
        EngineContract(
            name="lesson_player",
            version="1.0.0",
            responsibilities=["lesson rendering", "segment delivery"],
            outputs=["exports/lesson_player"],
        ),
        EngineContract(
            name="track_engine",
            version="1.0.0",
            responsibilities=["track definitions", "pathway orchestration"],
            outputs=["exports/tracks"],
        ),
        EngineContract(
            name="learning_analytics_engine",
            version="1.0.0",
            responsibilities=["active learning metrics", "volunteer logs", "admin rollups"],
            required_paths=["data/progress", "data/analytics"],
            outputs=["exports/analytics"],
        ),
        EngineContract(
            name="civic_intelligence_system",
            version="1.0.0",
            responsibilities=["unified civic intelligence exports", "dashboard snapshots"],
            outputs=["exports/civic_intelligence"],
        ),
    ]
