import sys
from pathlib import Path
import json

# Ensure project root is on path
sys.path.append(str(Path(__file__).resolve().parents[1]))

from engine.query_engine.graph_query_engine import GraphQueryEngine
from engine.query_engine.influence_analyzer import InfluenceAnalyzer


# --------------------------------------------------
# LOAD GRAPH DATA
# --------------------------------------------------

def load_graph():
    base_path = Path("exports/graph_persistence")

    nodes_path = base_path / "phase_07_nodes.json"
    edges_path = base_path / "phase_07_edges.json"

    if not nodes_path.exists() or not edges_path.exists():
        raise FileNotFoundError("Graph persistence files not found. Run Phase 07 build first.")

    with open(nodes_path) as f:
        nodes = json.load(f)

    with open(edges_path) as f:
        edges = json.load(f)

    if not isinstance(nodes, list) or not isinstance(edges, list):
        raise ValueError("Graph data is not in expected list format.")

    return nodes, edges


# --------------------------------------------------
# AUTO-DETECT A VALID BILL
# --------------------------------------------------

def find_sample_bill(nodes):
    for n in nodes:
        if n.get("node_type") == "bill":
            return n["id"]
    return None


# --------------------------------------------------
# SAFE NODE DISPLAY
# --------------------------------------------------

def format_node(engine, node_id):
    node = engine.get_node(node_id)
    if not node:
        return f"{node_id} (unknown)"

    name = node.get("name", "Unnamed")
    node_type = node.get("node_type", "unknown")

    return f"{name} ({node_type})"


# --------------------------------------------------
# MAIN EXECUTION
# --------------------------------------------------

def main():
    print("\n========================================")
    print(" Arkansas Civic Graph - Influence Engine")
    print("========================================\n")

    nodes, edges = load_graph()

    print(f"[INFO] Nodes loaded: {len(nodes)}")
    print(f"[INFO] Edges loaded: {len(edges)}")

    engine = GraphQueryEngine(nodes, edges)
    analyzer = InfluenceAnalyzer(engine)

    # Auto-select a valid bill
    bill_id = find_sample_bill(nodes)

    if not bill_id:
        print("\n[WARNING] No bill nodes found in dataset.")
        return

    print(f"\n[INFO] Using bill: {bill_id}")

    result = analyzer.bill_influence(bill_id)

    if not result:
        print("\n[WARNING] No influence relationships found.")
        return

    print("\n=== BILL INFLUENCE (TOP 10) ===\n")

    for r in result[:10]:
        label = format_node(engine, r["node"])
        print(f"{label}: {r['score']}")

    print("\n========================================")
    print(" Influence analysis complete")
    print("========================================\n")


# --------------------------------------------------
# ENTRY POINT
# --------------------------------------------------

if __name__ == "__main__":
    main()