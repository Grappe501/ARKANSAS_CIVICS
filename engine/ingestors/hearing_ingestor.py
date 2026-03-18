
from pathlib import Path

class HearingIngestor:
    name = "Committee Hearings"

    def ingest(self, data_dir):
        path = Path(data_dir) / "hearings"

        records = []

        if not path.exists():
            return records

        for file in path.glob("*.txt"):
            records.append({
                "type": "hearing_transcript",
                "source": str(file),
                "title": file.stem,
                "summary": "Committee hearing transcript ingested"
            })

        return records
