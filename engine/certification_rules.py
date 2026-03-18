from __future__ import annotations

from pathlib import Path
from typing import Any
import json
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from engine.platform_kernel import create_kernel  # noqa: E402
from engine.progress_registry import ProgressRegistry, safe_slug  # noqa: E402


class CertificationRulesEngine:
    """
    Rule evaluator for badges, certificates, and leadership tiers.
    """

    def __init__(self, root: str | Path | None = None) -> None:
        self.kernel = create_kernel(root)
        self.root = self.kernel.root
        self.registry = ProgressRegistry(root)
        self.config_dir = self.kernel.root / "config"
        self.rules_path = self.config_dir / "certification_tiers.json"

    def load_rules(self) -> dict[str, Any]:
        if not self.rules_path.exists():
            return {"tiers": [], "badges": [], "certifications": []}
        return json.loads(self.rules_path.read_text(encoding="utf-8"))

    def evaluate_learner(self, learner_id: str) -> dict[str, Any]:
        rules = self.load_rules()
        profile = self.registry.load_profile(learner_id)

        earned_badges = set(profile.earned_badges)
        earned_certifications = set(profile.earned_certifications)
        awarded_badges = []
        awarded_certifications = []
        updated_tier = profile.leadership_tier

        completed_courses = sum(1 for c in profile.courses.values() if c.status == "completed")
        learning_hours = profile.learning_hours_total
        approved_hours = profile.approved_action_hours_total

        for badge in rules.get("badges", []):
            slug = safe_slug(badge["slug"])
            if slug in earned_badges:
                continue
            if self._meets_requirements(badge, completed_courses, learning_hours, approved_hours):
                self.registry.add_badge(learner_id, slug)
                awarded_badges.append(slug)
                earned_badges.add(slug)

        for cert in rules.get("certifications", []):
            slug = safe_slug(cert["slug"])
            if slug in earned_certifications:
                continue
            if self._meets_requirements(cert, completed_courses, learning_hours, approved_hours):
                self.registry.add_certification(learner_id, slug)
                awarded_certifications.append(slug)
                earned_certifications.add(slug)

        for tier in sorted(rules.get("tiers", []), key=lambda x: x.get("rank", 0)):
            if self._meets_requirements(tier, completed_courses, learning_hours, approved_hours):
                updated_tier = safe_slug(tier["slug"])

        self.registry.set_leadership_tier(learner_id, updated_tier)

        return {
            "learner_id": learner_id,
            "awarded_badges": awarded_badges,
            "awarded_certifications": awarded_certifications,
            "leadership_tier": updated_tier,
            "completed_courses": completed_courses,
            "learning_hours_total": learning_hours,
            "approved_action_hours_total": approved_hours,
        }

    def _meets_requirements(
        self,
        rule: dict[str, Any],
        completed_courses: int,
        learning_hours: float,
        approved_hours: float,
    ) -> bool:
        min_courses = int(rule.get("min_completed_courses", 0))
        min_learning_hours = float(rule.get("min_learning_hours", 0.0))
        min_approved_action_hours = float(rule.get("min_approved_action_hours", 0.0))

        return (
            completed_courses >= min_courses
            and learning_hours >= min_learning_hours
            and approved_hours >= min_approved_action_hours
        )
