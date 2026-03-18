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


import argparse
import json


import sys
import os


from dotenv import load_dotenv

from engine.graph_persistence.supabase_connector import SupabaseConnector


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Query persisted Arkansas civic graph relationships.")
    parser.add_argument("--relationship", dest="relationship", default=None)
    parser.add_argument("--limit", dest="limit", type=int, default=20)
    return parser


def main() -> None:
    load_dotenv()
    args = build_parser().parse_args()
    connector = SupabaseConnector()
    rows = connector.select_relationships(relationship_type=args.relationship, limit=args.limit)
    print(json.dumps({"count": len(rows), "rows": rows}, indent=2))


if __name__ == "__main__":
    main()