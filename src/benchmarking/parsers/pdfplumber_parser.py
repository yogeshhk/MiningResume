"""
pdfplumber parser.

Precise PDF text and table extraction using pdfplumber (wraps pdfminer.six).
Particularly good at multi-column layouts and embedded tables.
Install: pip install pdfplumber
"""

from pathlib import Path
from .base_parser import BaseParser


class PDFPlumberParser(BaseParser):
    name = "pdfplumber"

    SUPPORTED = {".pdf"}

    def __init__(self):
        import pdfplumber  # noqa: F401 — import check
        self._pdfplumber = pdfplumber

    def supports(self, path: Path) -> bool:
        return Path(path).suffix.lower() in self.SUPPORTED

    def _parse(self, path: Path) -> str:
        pages_text = []
        with self._pdfplumber.open(str(path)) as pdf:
            for page in pdf.pages:
                text = page.extract_text() or ""
                # Also capture any tables as simple TSV blocks
                for table in page.extract_tables():
                    rows = ["\t".join(str(cell or "") for cell in row) for row in table]
                    text += "\n" + "\n".join(rows)
                pages_text.append(text)
        return "\n\n".join(pages_text)
