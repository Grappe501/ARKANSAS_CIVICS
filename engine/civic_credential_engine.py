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
from engine.progress_registry import ProgressRegistry  # noqa: E402
from engine.certification_rules import CertificationRulesEngine  # noqa: E402


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


class CivicCredentialEngine:
    """
    Unified credential snapshot for learner advancement.
    Produces credential exports that can later be promoted into database tables.
    """

    def __init__(self, root: str | Path | None = None) -> None:
        self.kernel = create_kernel(root)
        self.root = self.kernel.root
        self.registry = ProgressRegistry(root)
        self.rules = CertificationRulesEngine(root)
        self.export_dir = self.kernel.ensure_export_dir("credentials")
        self.export_dir.mkdir(parents=True, exist_ok=True)

    def build_learner_credential(self, learner_id: str) -> dict[str, Any]:
        rule_eval = self.rules.evaluate_learner(learner_id)
        profile = self.registry.load_profile(learner_id)

        payload = {
            "generated_at": utc_now_iso(),
            "learner_id": learner_id,
            "leadership_tier": profile.leadership_tier,
            "earned_badges": profile.earned_badges,
            "earned_certifications": profile.earned_certifications,
            "learning_hours_total": profile.learning_hours_total,
            "approved_action_hours_total": profile.approved_action_hours_total,
            "completed_courses": [
                c.course_slug for c in profile.courses.values() if c.status == "completed"
            ],
            "enrolled_tracks": profile.enrolled_tracks,
            "completed_tracks": profile.completed_tracks,
            "rule_evaluation": rule_eval,
            "database_connected": False,
        }

        path = self.export_dir / f"{learner_id}_credential.json"
        path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        return payload

    def export_index(self) -> list[Path]:
        learners = []
        for learner_id in self.registry.learner_index():
            learners.append(self.build_learner_credential(learner_id))

        index = {
            "generated_at": utc_now_iso(),
            "engine": "civic_credential_engine",
            "learner_count": len(learners),
            "database_connected": False,
            "credentials": learners,
        }

        json_path = self.export_dir / "credential_index.json"
        md_path = self.export_dir / "credential_report.md"

        json_path.write_text(json.dumps(index, indent=2), encoding="utf-8")
        md_path.write_text(self.render_markdown(index), encoding="utf-8")
        return [json_path, md_path]

    def render_markdown(self, index: dict[str, Any]) -> str:
        lines = [
            "# Arkansas Civics Credential Report",
            "",
            f"- Generated at: `{index['generated_at']}`",
            f"- Learners: **{index['learner_count']}**",
            "",
            "## Credentials",
            "",
        ]
        if not index["credentials"]:
            lines.append("_No credential records available yet._")
            return "\n".join(lines)

        for credential in index["credentials"]:
            lines.extend([
                f"### {credential['learner_id']}",
                f"- Leadership tier: {credential['leadership_tier']}",
                f"- Learning hours: {credential['learning_hours_total']}",
                f"- Approved civic action hours: {credential['approved_action_hours_total']}",
                f"- Badges: {len(credential['earned_badges'])}",
                f"- Certifications: {len(credential['earned_certifications'])}",
                "",
            ])
        return "\n".join(lines)
