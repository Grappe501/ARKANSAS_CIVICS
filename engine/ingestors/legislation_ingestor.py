
from pathlib import Path

class LegislationIngestor:
    name = "Arkansas Legislation"

    def ingest(self, data_dir):
        path = Path(data_dir) / "legislation"

        records = []

        if not path.exists():
            return records

        for file in path.glob("*.json"):
            records.append({
                "type": "legislation",
                "source": str(file),
                "title": file.stem,
                "summary": "Legislation record ingested"
            })

        return records
