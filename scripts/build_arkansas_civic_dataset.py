#!/usr/bin/env python3
from __future__ import annotations

"""
Single-command Arkansas civic dataset builder using Open States API v3.

Requires:
- OPENSTATES_API_KEY in the environment
- requests installed

Writes:
- data/openstates_arkansas/raw/*.json
- data/openstates_arkansas/normalized/*.json
- data/legislators/arkansas_legislators.json
- data/committees/arkansas_committees.json
- data/bills/arkansas_bills.json
- exports/graph_expansion/civic_graph_expansion.json
- exports/graph_persistence/phase_07_nodes.json
- exports/graph_persistence/phase_07_edges.json
- exports/graph_persistence/phase_07_indexes.json

Notes:
- This version avoids scanning all jurisdictions.
- It directly requests Arkansas's jurisdiction record.
- It handles 429 rate limiting with automatic backoff/retry.
- It restores environment-variable API key usage.
"""

import argparse
import json
import os
import re
import time
from collections import Counter
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Set, Tuple

try:
    import requests
except ImportError as exc:
    raise SystemExit("Missing dependency 'requests'. Install with: pip install requests") from exc

API_ROOT = "https://v3.openstates.org"
STATE_NAME = "Arkansas"
ARKANSAS_JURISDICTION_ID = "ocd-jurisdiction/country:us/state:ar/government"

DEFAULT_TIMEOUT = 60
DEFAULT_PAGE_SIZE = 20
DEFAULT_PAUSE_SECONDS = 6.0
DEFAULT_MAX_RETRIES = 6

CHAMBER_CLASS_MAP = {
    "upper": "senate",
    "lower": "house",
    "legislature": "legislature",
    "committee": "committee",
}

RATE_LIMIT_STATUS_CODES = {429}


@dataclass
class BuildConfig:
    project_root: Path
    api_key: str
    bill_limit: Optional[int]
    page_size: int
    pause_seconds: float
    active_sessions_only: bool
    max_retries: int


class OpenStatesClient:
    def __init__(
        self,
        api_key: str,
        page_size: int = DEFAULT_PAGE_SIZE,
        pause_seconds: float = DEFAULT_PAUSE_SECONDS,
        max_retries: int = DEFAULT_MAX_RETRIES,
    ):
        self.session = requests.Session()
        self.session.headers.update(
            {
                "X-API-KEY": api_key,
                "Accept": "application/json",
                "User-Agent": "ArkansasCivicsDatasetBuilder/1.1",
            }
        )
        self.page_size = page_size
        self.pause_seconds = pause_seconds
        self.max_retries = max_retries

    def _request(self, path: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        url = f"{API_ROOT.rstrip('/')}/{path.lstrip('/')}"
        params = params or {}

        attempt = 0
        while True:
            attempt += 1
            response = self.session.get(url, params=params, timeout=DEFAULT_TIMEOUT)

            if response.status_code in RATE_LIMIT_STATUS_CODES:
                if attempt > self.max_retries:
                    raise RuntimeError(
                        f"Open States API rate limit persisted after {self.max_retries} retries for {url}: "
                        f"{response.text[:500]}"
                    )

                retry_after_header = response.headers.get("Retry-After")
                if retry_after_header and retry_after_header.isdigit():
                    sleep_seconds = max(float(retry_after_header), self.pause_seconds)
                else:
                    sleep_seconds = max(self.pause_seconds, 6.0) * attempt

                print(
                    f"[RATE LIMIT] {response.status_code} for {path}. "
                    f"Retrying in {sleep_seconds:.1f}s (attempt {attempt}/{self.max_retries})..."
                )
                time.sleep(sleep_seconds)
                continue

            if response.status_code >= 400:
                raise RuntimeError(f"Open States API error {response.status_code} for {url}: {response.text[:500]}")

            data = response.json()
            if not isinstance(data, dict):
                raise RuntimeError(f"Unexpected API response shape for {url}: {type(data).__name__}")

            if self.pause_seconds > 0:
                time.sleep(self.pause_seconds)

            return data

    def fetch_paginated(
        self,
        path: str,
        params: Optional[Dict[str, Any]] = None,
        item_keys: Iterable[str] = ("results",),
    ) -> List[Dict[str, Any]]:
        params = dict(params or {})
        page = 1
        items_out: List[Dict[str, Any]] = []

        while True:
            params["page"] = page
            params["per_page"] = self.page_size
            payload = self._request(path, params)

            items = None
            for key in item_keys:
                if isinstance(payload.get(key), list):
                    items = payload[key]
                    break

            if items is None:
                for value in payload.values():
                    if isinstance(value, list) and (not value or isinstance(value[0], dict)):
                        items = value
                        break

            if items is None:
                items = []

            items_out.extend(items)

            pagination = payload.get("pagination") or {}
            next_page = pagination.get("next_page") or payload.get("next_page")

            if next_page:
                page = int(next_page)
                continue

            if len(items) < self.page_size:
                break

            page += 1

        return items_out


def ensure_dir(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    return path


def write_json(path: Path, payload: Any) -> None:
    ensure_dir(path.parent)
    with path.open("w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, ensure_ascii=False)


def slugify(value: str) -> str:
    value = (value or "").strip().lower()
    value = re.sub(r"[^a-z0-9]+", "-", value)
    return value.strip("-") or "unknown"


def stable_node_id(node_type: str, raw_id: str) -> str:
    return f"{node_type}:{raw_id}"


def unique_by_key(items: Iterable[Dict[str, Any]], key: str) -> List[Dict[str, Any]]:
    seen: Set[Any] = set()
    out: List[Dict[str, Any]] = []
    for item in items:
        value = item.get(key)
        if value in seen or value is None:
            continue
        seen.add(value)
        out.append(item)
    return out


def pick_current_role(person: Dict[str, Any]) -> Dict[str, Any]:
    role = person.get("current_role")
    if isinstance(role, dict):
        return role

    roles = person.get("roles") or []
    if isinstance(roles, list):
        for r in roles:
            if isinstance(r, dict) and r.get("current", True):
                return r
        for r in roles:
            if isinstance(r, dict):
                return r

    return {}


def extract_sessions(jurisdiction: Dict[str, Any], active_only: bool = True) -> List[Dict[str, Any]]:
    sessions = jurisdiction.get("legislative_sessions") or jurisdiction.get("sessions") or []
    out = []

    for session in sessions:
        if not isinstance(session, dict):
            continue
        if active_only and not session.get("active", False):
            continue

        out.append(
            {
                "id": session.get("identifier") or session.get("name") or session.get("id"),
                "identifier": session.get("identifier") or session.get("name") or session.get("id"),
                "name": session.get("name") or session.get("identifier") or session.get("id"),
                "classification": session.get("classification"),
                "start_date": session.get("start_date"),
                "end_date": session.get("end_date"),
                "active": bool(session.get("active")),
            }
        )

    return out


def normalize_legislator(person: Dict[str, Any]) -> Dict[str, Any]:
    role = pick_current_role(person)

    party = None
    parties = person.get("party") or person.get("parties")
    if isinstance(parties, str):
        party = parties
    elif isinstance(parties, list) and parties:
        first = parties[0]
        if isinstance(first, dict):
            party = first.get("name") or first.get("party")
        elif isinstance(first, str):
            party = first

    chamber_key = (role.get("org_classification") or role.get("organization_classification") or "").lower()
    chamber = CHAMBER_CLASS_MAP.get(chamber_key, chamber_key or None)

    return {
        "id": person.get("id"),
        "name": person.get("name"),
        "party": party,
        "district": role.get("district"),
        "chamber": chamber,
        "email": person.get("email"),
        "image": person.get("image"),
        "current_role": role,
        "links": person.get("links") or [],
        "sources": person.get("sources") or [],
        "raw": person,
    }


def normalize_committee(committee: Dict[str, Any]) -> Dict[str, Any]:
    memberships = []

    for m in committee.get("memberships") or committee.get("current_memberships") or []:
        if not isinstance(m, dict):
            continue
        person = m.get("person") or m.get("member") or {}
        memberships.append(
            {
                "person_id": person.get("id") or m.get("person_id"),
                "name": person.get("name") or m.get("name"),
                "role": m.get("role") or m.get("classification"),
            }
        )

    parent = committee.get("parent") or {}

    classification = committee.get("classification")
    chamber_key = classification.lower() if isinstance(classification, str) else ""

    return {
        "id": committee.get("id"),
        "name": committee.get("name"),
        "classification": classification,
        "chamber": CHAMBER_CLASS_MAP.get(chamber_key, classification),
        "memberships": memberships,
        "parent_id": parent.get("id"),
        "parent_name": parent.get("name"),
        "links": committee.get("links") or [],
        "sources": committee.get("sources") or [],
        "raw": committee,
    }


def normalize_bill(bill: Dict[str, Any]) -> Dict[str, Any]:
    sponsorships = []

    for s in bill.get("sponsorships") or []:
        if not isinstance(s, dict):
            continue
        person = s.get("person") or {}
        org = s.get("organization") or {}
        sponsorships.append(
            {
                "name": s.get("name") or person.get("name") or org.get("name"),
                "person_id": person.get("id"),
                "organization_id": org.get("id"),
                "classification": s.get("classification"),
                "primary": s.get("primary"),
            }
        )

    subjects = bill.get("subject") or bill.get("subjects") or []
    if isinstance(subjects, str):
        subjects = [subjects]
    else:
        subjects = [x for x in subjects if isinstance(x, str)]

    actions = []
    for action in bill.get("actions") or []:
        if not isinstance(action, dict):
            continue
        organization = action.get("organization") or {}
        actions.append(
            {
                "date": action.get("date"),
                "description": action.get("description"),
                "organization": organization.get("name") if isinstance(organization, dict) else str(organization),
                "classification": action.get("classification") or [],
            }
        )

    from_org = bill.get("from_organization") or {}
    from_org_classification = from_org.get("classification") if isinstance(from_org, dict) else None

    return {
        "id": bill.get("id"),
        "identifier": bill.get("identifier") or bill.get("bill_id"),
        "title": bill.get("title"),
        "session": bill.get("session") or bill.get("legislative_session"),
        "chamber": from_org_classification or bill.get("chamber"),
        "classification": bill.get("classification") or [],
        "subjects": subjects,
        "sponsorships": sponsorships,
        "actions": actions,
        "updated_at": bill.get("updated_at"),
        "openstates_url": bill.get("openstates_url") or bill.get("openstatesUrl"),
        "sources": bill.get("sources") or [],
        "raw": bill,
    }


def infer_committee_refs_from_bill(bill: Dict[str, Any], committees: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    index = {c["name"].lower(): c for c in committees if c.get("name")}
    refs = []

    for action in bill.get("actions") or []:
        text = " ".join(
            str(x)
            for x in [
                action.get("description"),
                action.get("organization"),
                " ".join(action.get("classification") or []),
            ]
            if x
        ).lower()

        if not text:
            continue

        for cname, committee in index.items():
            if cname in text:
                refs.append(
                    {
                        "committee_id": committee["id"],
                        "committee_name": committee["name"],
                        "reason": "action_text_match",
                    }
                )

    seen = set()
    out = []
    for ref in refs:
        key = ref["committee_id"]
        if key in seen:
            continue
        seen.add(key)
        out.append(ref)

    return out


def detect_arkansas_jurisdiction(client: OpenStatesClient) -> Dict[str, Any]:
    return client._request(f"/jurisdictions/{ARKANSAS_JURISDICTION_ID}")


def fetch_people(client: OpenStatesClient) -> List[Dict[str, Any]]:
    return client.fetch_paginated("/people", {"jurisdiction": STATE_NAME})


def fetch_committees(client: OpenStatesClient) -> List[Dict[str, Any]]:
    return client.fetch_paginated("/committees", {"jurisdiction": STATE_NAME})


def fetch_bills(
    client: OpenStatesClient,
    sessions: List[Dict[str, Any]],
    bill_limit: Optional[int],
) -> List[Dict[str, Any]]:
    out: List[Dict[str, Any]] = []

    for session in sessions:
        session_id = session["identifier"]
        if not session_id:
            continue

        session_bills = client.fetch_paginated("/bills", {"jurisdiction": STATE_NAME, "session": session_id})
        out.extend(session_bills)

        if bill_limit is not None and len(out) >= bill_limit:
            return out[:bill_limit]

    return out[:bill_limit] if bill_limit is not None else out


def build_graph(
    jurisdiction: Dict[str, Any],
    sessions: List[Dict[str, Any]],
    legislators: List[Dict[str, Any]],
    committees: List[Dict[str, Any]],
    bills: List[Dict[str, Any]],
) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    nodes: Dict[str, Dict[str, Any]] = {}
    edges: Dict[str, Dict[str, Any]] = {}

    def add_node(node_type: str, raw_id: str, label: str, metadata: Optional[Dict[str, Any]] = None) -> str:
        node_id = stable_node_id(node_type, raw_id)
        if node_id not in nodes:
            nodes[node_id] = {
                "id": node_id,
                "node_type": node_type,
                "name": label,
                "metadata": metadata or {},
            }
        elif metadata:
            nodes[node_id]["metadata"].update(
                {k: v for k, v in metadata.items() if v not in (None, "", [], {})}
            )
        return node_id

    def add_edge(
        source: str,
        target: str,
        rel: str,
        metadata: Optional[Dict[str, Any]] = None,
        weight: float = 1.0,
    ) -> None:
        edge_id = f"{source}|{rel}|{target}"
        if edge_id not in edges:
            edges[edge_id] = {
                "id": edge_id,
                "source": source,
                "target": target,
                "relationship_type": rel,
                "weight": weight,
                "metadata": metadata or {},
            }
        elif metadata:
            edges[edge_id]["metadata"].update(
                {k: v for k, v in metadata.items() if v not in (None, "", [], {})}
            )

    state_id = jurisdiction.get("id") or ARKANSAS_JURISDICTION_ID
    state_node = add_node(
        "organization",
        str(state_id),
        jurisdiction.get("name") or STATE_NAME,
        {
            "classification": "jurisdiction",
            "url": jurisdiction.get("url"),
        },
    )

    for session in sessions:
        session_identifier = str(session["identifier"])
        snode = add_node("session", session_identifier, str(session["name"]), session)
        add_edge(snode, state_node, "belongs_to", {"source": "openstates"})

    for person in legislators:
        if not person.get("id"):
            continue

        pnode = add_node(
            "legislator",
            person["id"],
            person.get("name") or person["id"],
            {
                "party": person.get("party"),
                "district": person.get("district"),
                "chamber": person.get("chamber"),
                "email": person.get("email"),
            },
        )
        add_edge(
            pnode,
            state_node,
            "serves_in",
            {"district": person.get("district"), "chamber": person.get("chamber")},
        )

        if person.get("chamber"):
            chamber_id = f"arkansas-{person['chamber']}"
            chamber_node = add_node(
                "organization",
                chamber_id,
                f"Arkansas {person['chamber'].title()}",
                {"classification": person["chamber"]},
            )
            add_edge(pnode, chamber_node, "member_of", {"source": "current_role"})
            add_edge(chamber_node, state_node, "part_of", {"source": "derived"})

    for committee in committees:
        if not committee.get("id"):
            continue

        cnode = add_node(
            "committee",
            committee["id"],
            committee.get("name") or committee["id"],
            {
                "classification": committee.get("classification"),
                "chamber": committee.get("chamber"),
                "parent_name": committee.get("parent_name"),
            },
        )
        add_edge(cnode, state_node, "part_of", {"source": "openstates"})

        if committee.get("chamber"):
            chamber_id = f"arkansas-{committee['chamber']}"
            chamber_node = add_node(
                "organization",
                chamber_id,
                f"Arkansas {committee['chamber'].title()}",
                {"classification": committee["chamber"]},
            )
            add_edge(cnode, chamber_node, "belongs_to", {"source": "committee_classification"})

        for membership in committee.get("memberships") or []:
            person_id = membership.get("person_id")
            if not person_id:
                continue

            pnode = add_node("legislator", person_id, membership.get("name") or person_id, {})
            add_edge(
                pnode,
                cnode,
                "member_of",
                {"role": membership.get("role") or "member", "source": "committee_membership"},
            )

    for bill in bills:
        bill_id = bill.get("id") or bill.get("identifier")
        if not bill_id:
            continue

        bnode = add_node(
            "bill",
            bill_id,
            bill.get("identifier") or bill.get("title") or bill_id,
            {
                "title": bill.get("title"),
                "session": bill.get("session"),
                "classification": bill.get("classification"),
                "openstates_url": bill.get("openstates_url"),
            },
        )
        add_edge(bnode, state_node, "introduced_in", {"source": "openstates"})

        if bill.get("session"):
            snode = add_node("session", str(bill["session"]), str(bill["session"]), {})
            add_edge(bnode, snode, "in_session", {"source": "bill.session"})

        for subject in bill.get("subjects") or []:
            subj_id = slugify(subject)
            subj_node = add_node("policy_area", subj_id, subject, {})
            add_edge(bnode, subj_node, "about", {"source": "bill.subjects"})

        for sponsor in bill.get("sponsorships") or []:
            person_id = sponsor.get("person_id")
            sponsor_name = sponsor.get("name")

            if person_id:
                pnode = add_node("legislator", person_id, sponsor_name or person_id, {})
                add_edge(
                    pnode,
                    bnode,
                    "sponsors",
                    {
                        "classification": sponsor.get("classification"),
                        "primary": sponsor.get("primary"),
                        "source": "bill.sponsorships",
                    },
                )
            elif sponsor_name:
                onode = add_node(
                    "organization",
                    slugify(sponsor_name),
                    sponsor_name,
                    {"classification": "sponsoring_entity"},
                )
                add_edge(
                    onode,
                    bnode,
                    "sponsors",
                    {
                        "classification": sponsor.get("classification"),
                        "primary": sponsor.get("primary"),
                    },
                )

        for ref in infer_committee_refs_from_bill(bill, committees):
            cnode = add_node("committee", ref["committee_id"], ref["committee_name"], {})
            add_edge(bnode, cnode, "referred_to", {"reason": ref["reason"]})

    return list(nodes.values()), list(edges.values())


def write_markdown_summary(path: Path, manifest: Dict[str, Any]) -> None:
    lines = [
        "# Arkansas Civic Dataset Build Summary",
        "",
        f"Generated: {manifest['generated_at']}",
        "",
        "## Dataset Counts",
    ]

    for key, value in manifest["dataset_counts"].items():
        lines.append(f"- {key}: {value}")

    lines.extend(["", "## Graph Counts"])
    for key, value in manifest["graph_counts"].items():
        if isinstance(value, dict):
            lines.append(f"- {key}:")
            for subkey, subvalue in value.items():
                lines.append(f"  - {subkey}: {subvalue}")
        else:
            lines.append(f"- {key}: {value}")

    path.write_text("\n".join(lines), encoding="utf-8")


def build_dataset(config: BuildConfig) -> Dict[str, Any]:
    data_root = ensure_dir(config.project_root / "data")
    exports_root = ensure_dir(config.project_root / "exports")
    dataset_root = ensure_dir(data_root / "openstates_arkansas")
    raw_root = ensure_dir(dataset_root / "raw")
    normalized_root = ensure_dir(dataset_root / "normalized")
    graph_export_root = ensure_dir(exports_root / "graph_expansion")
    graph_persistence_root = ensure_dir(exports_root / "graph_persistence")

    client = OpenStatesClient(
        config.api_key,
        page_size=config.page_size,
        pause_seconds=config.pause_seconds,
        max_retries=config.max_retries,
    )

    print("[INFO] Fetching Arkansas jurisdiction...")
    jurisdiction = detect_arkansas_jurisdiction(client)

    sessions = extract_sessions(jurisdiction, active_only=config.active_sessions_only)
    if not sessions:
        sessions = extract_sessions(jurisdiction, active_only=False)

    print(f"[INFO] Sessions found: {len(sessions)}")
    print("[INFO] Fetching legislators...")
    people_raw = fetch_people(client)
    print(f"[INFO] Legislator records fetched: {len(people_raw)}")

    print("[INFO] Fetching committees...")
    committees_raw = fetch_committees(client)
    print(f"[INFO] Committee records fetched: {len(committees_raw)}")

    print("[INFO] Fetching bills...")
    bills_raw = fetch_bills(client, sessions, config.bill_limit)
    print(f"[INFO] Bill records fetched: {len(bills_raw)}")

    legislators = unique_by_key([normalize_legislator(p) for p in people_raw], "id")
    committees = unique_by_key([normalize_committee(c) for c in committees_raw], "id")
    bills = unique_by_key([normalize_bill(b) for b in bills_raw], "id")

    nodes, edges = build_graph(jurisdiction, sessions, legislators, committees, bills)

    write_json(raw_root / "jurisdiction.json", jurisdiction)
    write_json(raw_root / "people.json", people_raw)
    write_json(raw_root / "committees.json", committees_raw)
    write_json(raw_root / "bills.json", bills_raw)

    write_json(normalized_root / "sessions.json", sessions)
    write_json(normalized_root / "legislators.json", legislators)
    write_json(normalized_root / "committees.json", committees)
    write_json(normalized_root / "bills.json", bills)
    write_json(
        normalized_root / "donors_placeholder.json",
        {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "records": [],
            "note": "Open States does not provide donor/campaign-finance data.",
        },
    )

    write_json(ensure_dir(data_root / "legislators") / "arkansas_legislators.json", legislators)
    write_json(ensure_dir(data_root / "committees") / "arkansas_committees.json", committees)
    write_json(ensure_dir(data_root / "bills") / "arkansas_bills.json", bills)
    write_json(
        ensure_dir(data_root / "donors") / "arkansas_donors_placeholder.json",
        {
            "records": [],
            "note": "Placeholder only. No donor data in Open States.",
        },
    )

    graph_export = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "engine": "arkansas_openstates_dataset_builder",
        "database_connected": False,
        "summary": {
            "node_count": len(nodes),
            "edge_count": len(edges),
            "expander_count": 1,
        },
        "reports": [
            {
                "name": "Arkansas Open States Build",
                "node_count": len(nodes),
                "edge_count": len(edges),
                "source_paths": [
                    str(raw_root / "people.json"),
                    str(raw_root / "committees.json"),
                    str(raw_root / "bills.json"),
                ],
            }
        ],
        "nodes": nodes,
        "edges": edges,
    }

    write_json(graph_export_root / "civic_graph_expansion.json", graph_export)
    write_json(graph_persistence_root / "phase_07_nodes.json", nodes)
    write_json(graph_persistence_root / "phase_07_edges.json", edges)
    write_json(
        graph_persistence_root / "phase_07_indexes.json",
        [
            {"index_key": "jurisdiction", "index_value": {"name": STATE_NAME}},
            {"index_key": "node_types", "index_value": dict(Counter(n["node_type"] for n in nodes))},
            {
                "index_key": "relationship_types",
                "index_value": dict(Counter(e["relationship_type"] for e in edges)),
            },
        ],
    )

    manifest = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "jurisdiction": jurisdiction.get("name") or STATE_NAME,
        "dataset_counts": {
            "sessions": len(sessions),
            "legislators": len(legislators),
            "committees": len(committees),
            "bills": len(bills),
        },
        "graph_counts": {
            "nodes": len(nodes),
            "edges": len(edges),
            "node_types": dict(Counter(n["node_type"] for n in nodes)),
            "edge_types": dict(Counter(e["relationship_type"] for e in edges)),
        },
        "notes": [
            "Donor data is not included because Open States does not provide campaign-finance records.",
            "Committee referrals are inferred from bill action text when committee names appear.",
            "Graph export is written directly to exports/graph_expansion/civic_graph_expansion.json.",
            "This builder directly fetches Arkansas jurisdiction and includes basic 429 retry logic.",
        ],
    }

    write_json(dataset_root / "build_manifest.json", manifest)
    write_markdown_summary(dataset_root / "build_summary.md", manifest)
    return manifest


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build Arkansas civic dataset and graph from Open States API v3.")
    parser.add_argument("--project-root", default=".", help="Path to Arkansas Civics project root.")
    parser.add_argument("--bill-limit", type=int, default=None, help="Optional cap on bills for faster test runs.")
    parser.add_argument("--page-size", type=int, default=DEFAULT_PAGE_SIZE, help="API page size. Default 50.")
    parser.add_argument(
        "--pause-seconds",
        type=float,
        default=DEFAULT_PAUSE_SECONDS,
        help=f"Pause between API requests. Default {DEFAULT_PAUSE_SECONDS}.",
    )
    parser.add_argument("--all-sessions", action="store_true", help="Fetch all sessions, not just active ones.")
    parser.add_argument(
        "--max-retries",
        type=int,
        default=DEFAULT_MAX_RETRIES,
        help=f"Max retries on rate-limit responses. Default {DEFAULT_MAX_RETRIES}.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    api_key = os.getenv("OPENSTATES_API_KEY")

    if not api_key:
        raise SystemExit("Missing OPENSTATES_API_KEY. Set it before running this script.")

    manifest = build_dataset(
        BuildConfig(
            project_root=Path(args.project_root).resolve(),
            api_key=api_key,
            bill_limit=args.bill_limit,
            page_size=args.page_size,
            pause_seconds=args.pause_seconds,
            active_sessions_only=not args.all_sessions,
            max_retries=args.max_retries,
        )
    )

    print("=" * 48)
    print(" Arkansas Civic Dataset Build Complete")
    print("=" * 48)
    print(
        json.dumps(
            {
                "project_root": str(Path(args.project_root).resolve()),
                "dataset_counts": manifest["dataset_counts"],
                "graph_counts": {
                    "nodes": manifest["graph_counts"]["nodes"],
                    "edges": manifest["graph_counts"]["edges"],
                },
                "manifest": str(
                    Path(args.project_root).resolve() / "data" / "openstates_arkansas" / "build_manifest.json"
                ),
                "graph_export": str(
                    Path(args.project_root).resolve() / "exports" / "graph_expansion" / "civic_graph_expansion.json"
                ),
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())