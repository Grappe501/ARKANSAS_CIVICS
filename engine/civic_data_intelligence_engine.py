
import json
from pathlib import Path
from datetime import datetime

from .ingestors.legislation_ingestor import LegislationIngestor
from .ingestors.pdf_ingestor import PDFIngestor
from .ingestors.hearing_ingestor import HearingIngestor


class CivicDataIntelligenceEngine:
    """
    Phase 05 — Civic Data Intelligence Engine
    Converts raw civic sources into structured knowledge for:
    - courses
    - explainers
    - knowledge graph nodes
    - civic alerts
    """

    def __init__(self, project_root):
        self.root = Path(project_root)
        self.data_dir = self.root / "data" / "civic_sources"
        self.output_dir = self.root / "data" / "civic_processed"

        self.output_dir.mkdir(parents=True, exist_ok=True)

        self.ingestors = [
            LegislationIngestor(),
            HearingIngestor(),
            PDFIngestor(),
        ]

    def run(self):
        results = []

        for ingestor in self.ingestors:
            print(f"[INFO] Running ingestor: {ingestor.name}")
            records = ingestor.ingest(self.data_dir)

            for r in records:
                r["processed_at"] = datetime.utcnow().isoformat()

            results.extend(records)

        out_file = self.output_dir / "civic_intelligence_output.json"

        with open(out_file, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2)

        print("\n----------------------------------")
        print(" CIVIC DATA INTELLIGENCE COMPLETE")
        print("----------------------------------")
        print(f"Records generated: {len(results)}")
        print(f"Output: {out_file}")
