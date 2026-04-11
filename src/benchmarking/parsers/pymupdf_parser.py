"""
PyMuPDF parser (fitz).

Fast native PDF text extraction with layout-aware ordering.
Install: pip install pymupdf
"""

from pathlib import Path
from .base_parser import BaseParser


class PyMuPDFParser(BaseParser):
    name = "PyMuPDF"

    SUPPORTED = {".pdf"}

    def __init__(self):
        import fitz  # noqa: F401 — import check
        self._fitz = fitz

    def supports(self, path: Path) -> bool:
        return Path(path).suffix.lower() in self.SUPPORTED

    def _parse(self, path: Path) -> str:
        doc = self._fitz.open(str(path))
        pages = []
        for page in doc:
            # "text" mode preserves reading order
            pages.append(page.get_text("text"))
        doc.close()
        return "\n\n".join(pages)
