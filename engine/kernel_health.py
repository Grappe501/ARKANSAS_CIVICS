from __future__ import annotations

from pathlib import Path
from typing import Any
import json

from engine.kernel_contracts import get_core_engine_contracts


class KernelHealth:
    def __init__(self, kernel: Any) -> None:
        self.kernel = kernel

    def gather(self) -> dict[str, Any]:
        validation = self.kernel.validate_structure()
        contracts = [contract.to_dict() for contract in get_core_engine_contracts()]

        checks = {
            "project_root_exists": self.kernel.root.exists(),
            "content_dir_exists": self.kernel.content_dir.exists(),
            "courses_dir_exists": self.kernel.courses_dir.exists(),
            "exports_dir_exists": self.kernel.exports_dir.exists(),
            "data_dir_exists": self.kernel.data_dir.exists(),
            "dashboard_dir_exists": self.kernel.dashboard_dir.exists(),
            "config_dir_exists": self.kernel.config_dir.exists(),
            "logs_dir_exists": self.kernel.logs_dir.exists(),
        }

        status = "healthy"
        if not all(checks.values()) or not validation.get("ok", False):
            status = "warning"

        return {
            "status": status,
            "environment": self.kernel.environment_name,
            "checks": checks,
            "validation": validation,
            "contracts": contracts,
            "database_readiness": self.kernel.get_database_readiness_summary(),
        }

    def export(self, output_path: Path) -> Path:
        payload = self.gather()
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        return output_path
