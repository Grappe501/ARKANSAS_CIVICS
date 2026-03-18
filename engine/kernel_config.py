from __future__ import annotations

from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any
import json
import os


@dataclass
class KernelEnvironment:
    name: str = "local"
    debug: bool = True
    log_level: str = "INFO"
    filesystem_source_of_truth: bool = True
    database_enabled: bool = False
    dashboard_enabled: bool = True

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class KernelConfig:
    project_name: str
    environment: KernelEnvironment
    project_root: str
    content_dir: str
    courses_dir: str
    exports_dir: str
    data_dir: str
    docs_dir: str
    scripts_dir: str
    apps_dir: str
    dashboard_dir: str
    dashboard_content_dir: str
    dashboard_manifest_path: str
    netlify_dir: str
    config_dir: str
    engine_dir: str
    logs_dir: str
    temp_dir: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "project_name": self.project_name,
            "environment": self.environment.to_dict(),
            "project_root": self.project_root,
            "content_dir": self.content_dir,
            "courses_dir": self.courses_dir,
            "exports_dir": self.exports_dir,
            "data_dir": self.data_dir,
            "docs_dir": self.docs_dir,
            "scripts_dir": self.scripts_dir,
            "apps_dir": self.apps_dir,
            "dashboard_dir": self.dashboard_dir,
            "dashboard_content_dir": self.dashboard_content_dir,
            "dashboard_manifest_path": self.dashboard_manifest_path,
            "netlify_dir": self.netlify_dir,
            "config_dir": self.config_dir,
            "engine_dir": self.engine_dir,
            "logs_dir": self.logs_dir,
            "temp_dir": self.temp_dir,
        }


def _read_json_if_exists(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


def load_environment(root: Path) -> KernelEnvironment:
    config_dir = root / "config"
    defaults = _read_json_if_exists(config_dir / "kernel.defaults.json")
    env_name = os.getenv("ARK_CIVICS_ENV", defaults.get("environment", "local"))
    env_file = config_dir / f"kernel.{env_name}.json"
    env_payload = _read_json_if_exists(env_file)

    merged = {
        "name": env_name,
        "debug": defaults.get("debug", True),
        "log_level": defaults.get("log_level", "INFO"),
        "filesystem_source_of_truth": defaults.get("filesystem_source_of_truth", True),
        "database_enabled": defaults.get("database_enabled", False),
        "dashboard_enabled": defaults.get("dashboard_enabled", True),
    }
    merged.update(env_payload)

    if os.getenv("ARK_CIVICS_DEBUG") is not None:
        merged["debug"] = os.getenv("ARK_CIVICS_DEBUG", "true").lower() in {"1", "true", "yes", "on"}
    if os.getenv("ARK_CIVICS_LOG_LEVEL"):
        merged["log_level"] = os.getenv("ARK_CIVICS_LOG_LEVEL", "INFO")
    if os.getenv("ARK_CIVICS_DATABASE_ENABLED") is not None:
        merged["database_enabled"] = os.getenv("ARK_CIVICS_DATABASE_ENABLED", "false").lower() in {"1", "true", "yes", "on"}

    return KernelEnvironment(**merged)


def build_kernel_config(root: Path, project_name: str = "Arkansas Civics") -> KernelConfig:
    environment = load_environment(root)

    content_dir = root / "content"
    courses_dir = content_dir / "courses"
    exports_dir = root / "exports"
    data_dir = root / "data"
    docs_dir = root / "docs"
    scripts_dir = root / "scripts"
    apps_dir = root / "apps"
    dashboard_dir = apps_dir / "editor-dashboard"
    dashboard_content_dir = dashboard_dir / "content"
    dashboard_manifest_path = dashboard_dir / "content-manifest.json"
    netlify_dir = root / "netlify"
    config_dir = root / "config"
    engine_dir = root / "engine"
    logs_dir = root / "logs"
    temp_dir = root / "tmp"

    return KernelConfig(
        project_name=project_name,
        environment=environment,
        project_root=str(root),
        content_dir=str(content_dir),
        courses_dir=str(courses_dir),
        exports_dir=str(exports_dir),
        data_dir=str(data_dir),
        docs_dir=str(docs_dir),
        scripts_dir=str(scripts_dir),
        apps_dir=str(apps_dir),
        dashboard_dir=str(dashboard_dir),
        dashboard_content_dir=str(dashboard_content_dir),
        dashboard_manifest_path=str(dashboard_manifest_path),
        netlify_dir=str(netlify_dir),
        config_dir=str(config_dir),
        engine_dir=str(engine_dir),
        logs_dir=str(logs_dir),
        temp_dir=str(temp_dir),
    )
