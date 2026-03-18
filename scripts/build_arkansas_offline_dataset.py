#!/usr/bin/env python3
from __future__ import annotations

import json
import random
from pathlib import Path
from datetime import datetime
from collections import Counter

PROJECT_ROOT = Path(".").resolve()

EXPORT_GRAPH = PROJECT_ROOT / "exports/graph_expansion/civic_graph_expansion.json"
EXPORT_NODES = PROJECT_ROOT / "exports/graph_persistence/phase_07_nodes.json"
EXPORT_EDGES = PROJECT_ROOT / "exports/graph_persistence/phase_07_edges.json"
EXPORT_INDEX = PROJECT_ROOT / "exports/graph_persistence/phase_07_indexes.json"

def ensure(path):
    path.parent.mkdir(parents=True, exist_ok=True)
    return path

def node(nid, ntype, name, meta=None):
    return {
        "id": nid,
        "node_type": ntype,
        "name": name,
        "metadata": meta or {}
    }

def edge(src, tgt, rel, meta=None):
    return {
        "id": f"{src}|{rel}|{tgt}",
        "source": src,
        "target": tgt,
        "relationship_type": rel,
        "weight": 1.0,
        "metadata": meta or {}
    }

def build():
    nodes = []
    edges = []

    # --- STATE ---
    state_id = "org:arkansas"
    nodes.append(node(state_id, "organization", "Arkansas", {"type": "state"}))

    # --- CHAMBERS ---
    house = "org:arkansas_house"
    senate = "org:arkansas_senate"

    nodes += [
        node(house, "organization", "Arkansas House"),
        node(senate, "organization", "Arkansas Senate"),
    ]

    edges += [
        edge(house, state_id, "part_of"),
        edge(senate, state_id, "part_of"),
    ]

    # --- COMMITTEES ---
    committees = []
    for i in range(10):
        cid = f"committee:house_{i}"
        committees.append(cid)
        nodes.append(node(cid, "committee", f"House Committee {i}"))
        edges.append(edge(cid, house, "belongs_to"))

    for i in range(8):
        cid = f"committee:senate_{i}"
        committees.append(cid)
        nodes.append(node(cid, "committee", f"Senate Committee {i}"))
        edges.append(edge(cid, senate, "belongs_to"))

    # --- LEGISLATORS ---
    legislators = []
    for i in range(135):
        lid = f"legislator:{i}"
        chamber = house if i < 100 else senate
        legislators.append(lid)

        nodes.append(node(
            lid,
            "legislator",
            f"Legislator {i}",
            {
                "party": random.choice(["R", "D"]),
                "district": i,
            }
        ))

        edges.append(edge(lid, chamber, "member_of"))

        # assign to committee
        committee = random.choice(committees)
        edges.append(edge(lid, committee, "member_of"))

    # --- POLICY AREAS ---
    policies = ["Education", "Healthcare", "Taxes", "Infrastructure", "Energy"]
    policy_nodes = []

    for p in policies:
        pid = f"policy:{p.lower()}"
        policy_nodes.append(pid)
        nodes.append(node(pid, "policy_area", p))

    # --- BILLS ---
    bills = []
    for i in range(50):
        bid = f"bill:{i}"
        bills.append(bid)

        nodes.append(node(
            bid,
            "bill",
            f"HB{i}",
            {"title": f"Sample Bill {i}"}
        ))

        # link to state
        edges.append(edge(bid, state_id, "introduced_in"))

        # assign sponsor
        sponsor = random.choice(legislators)
        edges.append(edge(sponsor, bid, "sponsors"))

        # assign policy
        policy = random.choice(policy_nodes)
        edges.append(edge(bid, policy, "about"))

        # assign committee
        committee = random.choice(committees)
        edges.append(edge(bid, committee, "referred_to"))

    return nodes, edges

def main():
    print("Building OFFLINE Arkansas dataset...")

    nodes, edges = build()

    graph = {
        "generated_at": datetime.utcnow().isoformat(),
        "summary": {
            "node_count": len(nodes),
            "edge_count": len(edges)
        },
        "nodes": nodes,
        "edges": edges
    }

    ensure(EXPORT_GRAPH).write_text(json.dumps(graph, indent=2))
    ensure(EXPORT_NODES).write_text(json.dumps(nodes, indent=2))
    ensure(EXPORT_EDGES).write_text(json.dumps(edges, indent=2))

    ensure(EXPORT_INDEX).write_text(json.dumps([
        {"index_key": "node_types", "index_value": dict(Counter(n["node_type"] for n in nodes))},
        {"index_key": "edge_types", "index_value": dict(Counter(e["relationship_type"] for e in edges))}
    ], indent=2))

    print("=" * 50)
    print("OFFLINE DATASET BUILT")
    print("=" * 50)
    print(f"Nodes: {len(nodes)}")
    print(f"Edges: {len(edges)}")

if __name__ == "__main__":
    main()