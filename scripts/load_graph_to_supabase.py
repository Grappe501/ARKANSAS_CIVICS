from __future__ import annotations
import sys
import os

# Add project root to Python path
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)


import sys
import os

# Add project root to Python path


import json
import os
from pathlib import Path

import sys
import os



from dotenv import load_dotenv

from engine.graph_persistence.graph_ingestor import GraphIngestor
from engine.graph_persistence.supabase_connector import SupabaseConnector


def main() -> None:
    load_dotenv()
    project_root = Path(__file__).resolve().parents[1]
    default_graph = project_root / "exports" / "graph_expansion" / "civic_graph_expansion.json"
    graph_path = Path(os.getenv("GRAPH_SOURCE_PATH", str(default_graph)))

    if not graph_path.exists():
        raise FileNotFoundError(f"Graph source not found: {graph_path}")

    ingestor = GraphIngestor()
    payload = ingestor.load_and_normalize(graph_path)
    connector = SupabaseConnector()

    node_result = connector.upsert("civic_nodes", payload.nodes, on_conflict="id")
    edge_result = connector.upsert("civic_edges", payload.edges, on_conflict="id")
    index_rows = [
        {
            "index_key": row["index_key"],
            "index_group": row["index_group"],
            "payload": row["payload"],
        }
        for row in payload.indexes
    ]
    index_result = connector.upsert("civic_graph_index", index_rows, on_conflict="index_key")

    print("=" * 48)
    print(" Phase 07 - Supabase Graph Load Complete")
    print("=" * 48)
    print(json.dumps({
        "source_graph": str(graph_path),
        "results": [node_result, edge_result, index_result],
    }, indent=2))


if __name__ == "__main__":
    main()