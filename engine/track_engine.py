from __future__ import annotations

from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Any
import json
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from engine.course_engine import CourseEngine, CoursePackage  # noqa: E402
from engine.platform_kernel import create_kernel  # noqa: E402


@dataclass
class TrackCourseRef:
    course_slug: str
    course_title: str
    reason: str
    required: bool = True
    estimated_minutes: int = 0
    tags: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class TrackMilestone:
    slug: str
    title: str
    description: str
    level: int
    badge: str
    course_refs: list[TrackCourseRef] = field(default_factory=list)
    target_hours: float = 0.0

    @property
    def estimated_minutes(self) -> int:
        return sum(ref.estimated_minutes for ref in self.course_refs if ref.required)

    def to_dict(self) -> dict[str, Any]:
        return {
            "slug": self.slug,
            "title": self.title,
            "description": self.description,
            "level": self.level,
            "badge": self.badge,
            "target_hours": self.target_hours,
            "estimated_minutes": self.estimated_minutes,
            "course_refs": [ref.to_dict() for ref in self.course_refs],
        }


@dataclass
class TrackDefinition:
    slug: str
    title: str
    subtitle: str
    description: str
    audience: str
    focus_tags: list[str] = field(default_factory=list)
    milestones: list[TrackMilestone] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def course_count(self) -> int:
        seen = {ref.course_slug for milestone in self.milestones for ref in milestone.course_refs}
        return len(seen)

    @property
    def estimated_minutes(self) -> int:
        seen: dict[str, int] = {}
        for milestone in self.milestones:
            for ref in milestone.course_refs:
                if ref.required:
                    seen[ref.course_slug] = max(seen.get(ref.course_slug, 0), ref.estimated_minutes)
        return sum(seen.values())

    @property
    def estimated_hours(self) -> float:
        return round(self.estimated_minutes / 60, 1)

    def to_dict(self) -> dict[str, Any]:
        return {
            "slug": self.slug,
            "title": self.title,
            "subtitle": self.subtitle,
            "description": self.description,
            "audience": self.audience,
            "focus_tags": self.focus_tags,
            "course_count": self.course_count,
            "estimated_minutes": self.estimated_minutes,
            "estimated_hours": self.estimated_hours,
            "metadata": self.metadata,
            "milestones": [milestone.to_dict() for milestone in self.milestones],
        }


class TrackEngine:
    """
    Arkansas Civics Track Engine

    Purpose:
    - Build role-based learning pathways on top of the course engine
    - Support future progress tracking, volunteer hours, and AI-guided learning
    - Keep authored content in files while generating structured track definitions
    """

    def __init__(self, root: str | Path | None = None) -> None:
        self.kernel = create_kernel(root)
        self.course_engine = CourseEngine(root)
        self.root = self.kernel.root
        self._course_packages: dict[str, CoursePackage] | None = None

    # --------------------------------------------------------
    # Course package helpers
    # --------------------------------------------------------

    def get_course_packages(self) -> dict[str, CoursePackage]:
        if self._course_packages is None:
            packages = self.course_engine.build_all_course_packages()
            self._course_packages = {package.slug: package for package in packages}
        return self._course_packages

    def get_preferred_course_slugs(self) -> list[str]:
        packages = self.get_course_packages()
        preferred_groups = [
            ["course_01_civic_awakening"],
            ["course_02_arkansas_civic_history"],
            ["course_03_direct_democracy_and_the_ballot", "course_03_direct_democracy"],
            ["course_04_voting_systems_and_representation", "course_04_voting_systems"],
            ["course_05_labor_unions_and_collective_power", "course_05_labor_and_collective_power"],
            ["course_06_shared_pain_shared_story", "course_06_shared_pain"],
            ["course_07_coalitions_and_leadership", "course_07_shared_purpose"],
            ["course_08_messaging_media_and_narrative", "course_08_coalition_building"],
            ["course_09_strategy_petitions_and_campaigns", "course_09_messaging_and_media"],
            ["course_10_opposition_pushback_and_rule_changes", "course_10_strategy_and_campaigns"],
            ["course_11_the_reader_becomes_the_organizer", "course_11_opposition_and_pushback"],
            ["course_12_sustaining_the_ecosystem", "course_12_sustaining_movements"],
        ]

        selected: list[str] = []
        for group in preferred_groups:
            for slug in group:
                if slug in packages:
                    selected.append(slug)
                    break
        return selected

    def build_track_definitions(self) -> list[TrackDefinition]:
        self.kernel.assert_core_paths()
        packages = self.get_course_packages()
        preferred = set(self.get_preferred_course_slugs())

        def available(slug: str) -> bool:
            return slug in packages

        def pick(slug: str, fallback: str | None = None) -> str | None:
            if available(slug):
                return slug
            if fallback and available(fallback):
                return fallback
            return None

        direct = pick("course_03_direct_democracy_and_the_ballot", "course_03_direct_democracy")
        voting = pick("course_04_voting_systems_and_representation", "course_04_voting_systems")
        labor = pick("course_05_labor_unions_and_collective_power", "course_05_labor_and_collective_power")
        shared = pick("course_06_shared_pain_shared_story", "course_06_shared_pain")
        coalitions = pick("course_07_coalitions_and_leadership", "course_07_shared_purpose")
        narrative = pick("course_08_messaging_media_and_narrative", "course_08_coalition_building")
        strategy = pick("course_09_strategy_petitions_and_campaigns", "course_09_messaging_and_media")
        opposition = pick("course_10_opposition_pushback_and_rule_changes", "course_10_strategy_and_campaigns")
        organizer = pick("course_11_the_reader_becomes_the_organizer", "course_11_opposition_and_pushback")
        ecosystem = pick("course_12_sustaining_the_ecosystem", "course_12_sustaining_movements")

        tracks: list[TrackDefinition] = []

        tracks.append(
            self.build_track(
                slug="stand-up-arkansas-civic-foundations",
                title="Stand Up Arkansas Civic Foundations",
                subtitle="The launchpad for civic literacy, historical context, and Arkansas power analysis.",
                description=(
                    "A deep civic foundations pathway for learners who need the Arkansas context before choosing a more advanced role. "
                    "This track builds shared language, institutional literacy, and movement awareness."
                ),
                audience="New learners, students, volunteers, and community members entering the platform.",
                focus_tags=["foundations", "arkansas", "history", "civics"],
                milestones=[
                    self.milestone("orientation", "Orientation to Power", 1, "Foundation Scout", [
                        ("course_01_civic_awakening", "Establish the emotional and civic frame for the platform."),
                        ("course_02_arkansas_civic_history", "Understand Arkansas history as a civic power map."),
                    ]),
                    self.milestone("people-power", "People Power and Democratic Design", 2, "People Power Builder", [
                        (direct, "Understand ballot power, initiatives, and direct democracy."),
                        (voting, "Understand voting systems, representation, and access."),
                    ]),
                    self.milestone("movement-basics", "Movement Literacy", 3, "Movement Cartographer", [
                        (shared, "Translate pain into story and shared public meaning."),
                        (coalitions, "Learn coalition and servant leadership frameworks."),
                    ]),
                ],
                metadata={"public_track": True, "recommended_entry": True},
            )
        )

        tracks.append(
            self.build_track(
                slug="campaign-manager-path",
                title="Campaign Manager Path",
                subtitle="A systems-level leadership pathway for designing, staffing, and executing campaigns.",
                description=(
                    "Build the full civic and operational stack needed to lead local or statewide campaigns in Arkansas, "
                    "including strategy, narrative, field systems, rule changes, and long-term sustainability."
                ),
                audience="Campaign managers, field directors, chiefs of staff, organizers moving into leadership.",
                focus_tags=["campaigns", "strategy", "leadership", "management"],
                milestones=[
                    self.milestone("campaign-context", "Context and Terrain", 1, "Terrain Reader", [
                        ("course_01_civic_awakening", "Ground the learner in Arkansas civic realities."),
                        ("course_02_arkansas_civic_history", "Add the historical context behind present strategy."),
                    ]),
                    self.milestone("campaign-systems", "Campaign Systems", 2, "Campaign Architect", [
                        (strategy, "Learn issue selection, county strategy, petition systems, and campaign buildout."),
                        (narrative, "Develop message architecture and media discipline."),
                    ]),
                    self.milestone("pushback", "Opposition and Adaptation", 3, "Pressure Navigator", [
                        (opposition, "Understand backlash, legal gatekeeping, and movement adaptation."),
                        (organizer, "Translate strategy into scalable organizing systems."),
                    ]),
                    self.milestone("ecosystem", "Sustaining the Machine", 4, "Ecosystem Steward", [
                        (ecosystem, "Build durable infrastructure, replication, and long-tail systems."),
                        (coalitions, "Lead across organizations and stakeholders."),
                    ]),
                ],
                metadata={"career_track": True, "role": "campaign_manager"},
            )
        )

        tracks.append(
            self.build_track(
                slug="organizer-field-path",
                title="Organizer and Field Path",
                subtitle="A pathway for local leaders building people power, volunteer discipline, and public action.",
                description=(
                    "Train organizers to move from civic understanding into field work, coalition building, story discipline, "
                    "and durable local campaign operations."
                ),
                audience="Community organizers, volunteer leaders, church organizers, union leaders, field captains.",
                focus_tags=["organizing", "field", "volunteers", "leadership"],
                milestones=[
                    self.milestone("organizer-foundations", "Foundations for Organizing", 1, "Table Setter", [
                        ("course_01_civic_awakening", "Create a shared civic baseline."),
                        (shared, "Learn the story logic that binds people together."),
                    ]),
                    self.milestone("coalitions", "Coalitions and Leadership", 2, "Coalition Weaver", [
                        (coalitions, "Build coalition and servant leadership skills."),
                        (labor, "Study collective power and worker-centered organizing models."),
                    ]),
                    self.milestone("narrative-field", "Narrative and Field Discipline", 3, "Field Story Builder", [
                        (narrative, "Develop real-world narrative skills for public engagement."),
                        (organizer, "Build local campaign and issue infrastructure."),
                    ]),
                    self.milestone("resilience", "Pressure, Pushback, and Durability", 4, "Resilient Organizer", [
                        (opposition, "Learn how organizers adapt under pressure."),
                        (ecosystem, "Think beyond one campaign toward long-term civic infrastructure."),
                    ]),
                ],
                metadata={"career_track": True, "role": "organizer"},
            )
        )

        tracks.append(
            self.build_track(
                slug="arkansas-constitution-and-ballot-path",
                title="Arkansas Constitution and Ballot Path",
                subtitle="A specialized track for deep study of constitutional structure, ballot power, and democratic design.",
                description=(
                    "A deep-dive civic scholarship pathway focused on Arkansas constitutional history, ballot systems, "
                    "representation, and institutional design."
                ),
                audience="Researchers, lawyers, policy advocates, ballot leaders, constitution scholars.",
                focus_tags=["constitution", "ballot", "policy", "governance"],
                milestones=[
                    self.milestone("historical-frame", "Historical and Constitutional Frame", 1, "Constitution Reader", [
                        ("course_02_arkansas_civic_history", "Ground constitutional study in Arkansas history."),
                        (direct, "Understand amendment power and the ballot process."),
                    ]),
                    self.milestone("institutional-design", "Institutional Design", 2, "Democracy Designer", [
                        (voting, "Study representation systems and structural design choices."),
                        (strategy, "Connect constitutional change to practical campaign execution."),
                    ]),
                    self.milestone("gatekeeping", "Gatekeeping and Rule Changes", 3, "Rule Change Analyst", [
                        (opposition, "Analyze backlash, courts, and secretarial gatekeeping."),
                        (ecosystem, "Think structurally about long-term democratic maintenance."),
                    ]),
                ],
                metadata={"deep_dive": True, "specialty": "constitution"},
            )
        )

        tracks.append(
            self.build_track(
                slug="messaging-and-narrative-path",
                title="Messaging and Narrative Path",
                subtitle="A pathway for people shaping public meaning, movement identity, and Arkansas-facing persuasion.",
                description=(
                    "Train communicators to connect civic content, public story, media discipline, and message testing into a unified practice."
                ),
                audience="Communications leads, spokespeople, media strategists, educators, storytellers.",
                focus_tags=["messaging", "media", "story", "persuasion"],
                milestones=[
                    self.milestone("story-basics", "Story Foundations", 1, "Story Scout", [
                        (shared, "Understand the emotional architecture of public story."),
                        ("course_01_civic_awakening", "Anchor story in civic reality."),
                    ]),
                    self.milestone("message-design", "Message Design", 2, "Narrative Engineer", [
                        (narrative, "Study Arkansas narrative shaping, message design, and testing."),
                        (coalitions, "Align messaging with coalition leadership realities."),
                    ]),
                    self.milestone("campaign-application", "Campaign Application", 3, "Movement Messenger", [
                        (strategy, "Apply message systems to petition and campaign strategy."),
                        (opposition, "Study misinformation, counter-narratives, and movement discipline."),
                    ]),
                ],
                metadata={"career_track": True, "role": "communications"},
            )
        )

        tracks.append(
            self.build_track(
                slug="leadership-development-path",
                title="Leadership Development Path",
                subtitle="A pathway for servant leaders building long-term civic infrastructure in Arkansas.",
                description=(
                    "An advanced leadership track combining civic context, coalition stewardship, strategy, and ecosystem building."
                ),
                audience="Executive leaders, movement builders, organizational directors, coalition conveners.",
                focus_tags=["leadership", "servant-leadership", "ecosystem", "strategy"],
                milestones=[
                    self.milestone("leader-context", "Leadership Context", 1, "Context Steward", [
                        ("course_01_civic_awakening", "Ground leadership in Arkansas civic reality."),
                        ("course_02_arkansas_civic_history", "Understand the historical burden and opportunity of leadership."),
                    ]),
                    self.milestone("leader-coalitions", "Coalitions and Shared Purpose", 2, "Coalition Captain", [
                        (coalitions, "Develop coalition leadership and shared-purpose practice."),
                        (shared, "Learn how shared pain and shared story shape legitimacy."),
                    ]),
                    self.milestone("leader-strategy", "Strategy Under Pressure", 3, "Strategic Steward", [
                        (strategy, "Study execution, sequencing, and public strategy."),
                        (opposition, "Learn to lead through backlash and adaptation."),
                    ]),
                    self.milestone("leader-ecosystem", "Stewardship and Replication", 4, "Movement Steward", [
                        (ecosystem, "Build long-tail institutions and replicable public systems."),
                        (organizer, "Ensure leadership stays connected to real people and ground game."),
                    ]),
                ],
                metadata={"career_track": True, "role": "leader"},
            )
        )

        tracks.append(
            self.build_track(
                slug="arkansas-history-scholar-path",
                title="Arkansas History Scholar Path",
                subtitle="A pathway for learners who want deep historical context behind Arkansas civic life and public struggle.",
                description=(
                    "A historical-intelligence track focused on Arkansas civic history, labor, race, backlash, institutions, and memory."
                ),
                audience="Students, teachers, researchers, historians, public education leaders.",
                focus_tags=["history", "arkansas", "research", "public-memory"],
                milestones=[
                    self.milestone("history-core", "Arkansas Historical Core", 1, "History Witness", [
                        ("course_02_arkansas_civic_history", "Begin with the central historical course."),
                        (labor, "Study labor and collective power in historical context."),
                    ]),
                    self.milestone("history-structure", "History and Structure", 2, "Structure Historian", [
                        (voting, "Connect history to systems of representation."),
                        (direct, "Connect history to democratic design and ballot power."),
                    ]),
                    self.milestone("history-memory", "Story, Memory, and Continuity", 3, "Arkansas Memory Keeper", [
                        (shared, "Understand how pain becomes story and civic memory."),
                        (ecosystem, "Think about how history is preserved and taught over time."),
                    ]),
                ],
                metadata={"deep_dive": True, "specialty": "history"},
            )
        )

        return [track for track in tracks if track.course_count > 0 and any(ref.course_slug in preferred or True for m in track.milestones for ref in m.course_refs)]

    def build_track(self, slug: str, title: str, subtitle: str, description: str, audience: str,
                    focus_tags: list[str], milestones: list[TrackMilestone], metadata: dict[str, Any] | None = None) -> TrackDefinition:
        metadata = metadata or {}
        metadata.setdefault("generated_by", "engine.track_engine")
        metadata.setdefault("source_of_truth", "content/courses")
        return TrackDefinition(
            slug=slug,
            title=title,
            subtitle=subtitle,
            description=description,
            audience=audience,
            focus_tags=focus_tags,
            milestones=milestones,
            metadata=metadata,
        )

    def milestone(self, slug: str, title: str, level: int, badge: str,
                  course_specs: list[tuple[str | None, str]],
                  description: str | None = None) -> TrackMilestone:
        refs: list[TrackCourseRef] = []
        packages = self.get_course_packages()
        for course_slug, reason in course_specs:
            if not course_slug or course_slug not in packages:
                continue
            package = packages[course_slug]
            refs.append(
                TrackCourseRef(
                    course_slug=course_slug,
                    course_title=package.title,
                    reason=reason,
                    required=True,
                    estimated_minutes=package.total_estimated_minutes,
                    tags=list(package.metadata.get("focus_tags", [])) if isinstance(package.metadata, dict) else [],
                )
            )

        if description is None:
            description = f"Complete the {title.lower()} milestone by finishing the required Arkansas civics modules."

        return TrackMilestone(
            slug=slug,
            title=title,
            description=description,
            level=level,
            badge=badge,
            course_refs=refs,
            target_hours=round(sum(ref.estimated_minutes for ref in refs) / 60, 1),
        )

    # --------------------------------------------------------
    # Exports
    # --------------------------------------------------------

    def export_track_definitions(self, output_dir: Path | None = None) -> list[Path]:
        tracks = self.build_track_definitions()
        if output_dir is None:
            output_dir = self.kernel.ensure_export_dir("tracks")

        output_paths: list[Path] = []
        index_payload: dict[str, Any] = {
            "generated_by": "engine.track_engine",
            "track_count": len(tracks),
            "tracks": [],
        }

        for track in tracks:
            track_dir = output_dir / track.slug
            track_dir.mkdir(parents=True, exist_ok=True)

            json_path = track_dir / "track_definition.json"
            json_path.write_text(json.dumps(track.to_dict(), indent=2), encoding="utf-8")
            output_paths.append(json_path)

            md_path = track_dir / "track_definition.md"
            md_path.write_text(self.render_track_markdown(track), encoding="utf-8")
            output_paths.append(md_path)

            index_payload["tracks"].append(
                {
                    "slug": track.slug,
                    "title": track.title,
                    "subtitle": track.subtitle,
                    "course_count": track.course_count,
                    "estimated_minutes": track.estimated_minutes,
                    "estimated_hours": track.estimated_hours,
                    "audience": track.audience,
                    "focus_tags": track.focus_tags,
                    "milestone_count": len(track.milestones),
                }
            )

        index_path = output_dir / "track_index.json"
        index_path.write_text(json.dumps(index_payload, indent=2), encoding="utf-8")
        output_paths.append(index_path)

        return output_paths

    def render_track_markdown(self, track: TrackDefinition) -> str:
        lines: list[str] = [
            f"# {track.title}",
            "",
            track.subtitle,
            "",
            f"- Slug: `{track.slug}`",
            f"- Audience: {track.audience}",
            f"- Courses: {track.course_count}",
            f"- Estimated hours: {track.estimated_hours}",
            f"- Tags: {', '.join(track.focus_tags)}",
            "",
            "## Description",
            "",
            track.description,
            "",
        ]

        for milestone in track.milestones:
            lines.extend([
                f"## Level {milestone.level}: {milestone.title}",
                "",
                f"- Badge: {milestone.badge}",
                f"- Target hours: {milestone.target_hours}",
                "",
                milestone.description,
                "",
                "### Required Courses",
                "",
            ])

            for ref in milestone.course_refs:
                lines.extend([
                    f"- **{ref.course_title}** (`{ref.course_slug}`)",
                    f"  - Why it matters: {ref.reason}",
                    f"  - Estimated minutes: {ref.estimated_minutes}",
                ])
            lines.append("")

        return "\n".join(lines).strip() + "\n"


def build_and_export_tracks(root: str | Path | None = None) -> list[Path]:
    engine = TrackEngine(root=root)
    return engine.export_track_definitions()


if __name__ == "__main__":
    engine = TrackEngine()
    outputs = engine.export_track_definitions()
    tracks = engine.build_track_definitions()

    print("\n================================================")
    print(" Arkansas Civics Track Engine")
    print("================================================\n")
    print(f"Project root: {engine.root}")
    print(f"Tracks generated: {len(tracks)}")
    print("\nOutputs:")
    for path in outputs:
        print(path)
    print()
