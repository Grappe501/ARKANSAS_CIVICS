
from pathlib import Path

class PDFIngestor:
    name = "PDF Civic Documents"

    def ingest(self, data_dir):
        path = Path(data_dir) / "pdf"

        records = []

        if not path.exists():
            return records

        for file in path.glob("*.pdf"):
            records.append({
                "type": "pdf_document",
                "source": str(file),
                "title": file.stem,
                "summary": "PDF document ready for NLP processing"
            })

        return records
