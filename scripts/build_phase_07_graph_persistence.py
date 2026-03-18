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


def main() -> None:
    load_dotenv()
    project_root = Path(__file__).resolve().parents[1]
    default_graph = project_root / "exports" / "graph_expansion" / "civic_graph_expansion.json"
    graph_path = Path(os.getenv("GRAPH_SOURCE_PATH", str(default_graph)))
    export_dir = project_root / "exports" / "graph_persistence"

    if not graph_path.exists():
        raise FileNotFoundError(f"Graph source not found: {graph_path}")

    ingestor = GraphIngestor()
    payload = ingestor.load_and_normalize(graph_path)
    outputs = ingestor.write_build_artifacts(payload, export_dir)

    print("=" * 48)
    print(" Phase 07 - Civic Graph Persistence Build")
    print("=" * 48)
    print(json.dumps({
        "source_graph": str(graph_path),
        "outputs": outputs,
        "counts": {
            "nodes": len(payload.nodes),
            "edges": len(payload.edges),
            "indexes": len(payload.indexes),
        },
    }, indent=2))


if __name__ == "__main__":
    main()