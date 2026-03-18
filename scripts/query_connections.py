import sys
from pathlib import Path

# Ensure project root is on path
sys.path.append(str(Path(__file__).resolve().parents[1]))
import json
from engine.query_engine.graph_query_engine import GraphQueryEngine


def load_graph():
    with open("exports/graph_persistence/phase_07_nodes.json") as f:
        nodes = json.load(f)

    with open("exports/graph_persistence/phase_07_edges.json") as f:
        edges = json.load(f)

    return nodes, edges


def main():
    nodes, edges = load_graph()
    engine = GraphQueryEngine(nodes, edges)

    start = "legislator:1"

    connections = engine.traverse(start, depth=2)

    print("\n=== CONNECTIONS ===\n")
    for e in connections[:20]:
        print(f"{e['source']} --{e['relationship_type']}--> {e['target']}")


if __name__ == "__main__":
    main()