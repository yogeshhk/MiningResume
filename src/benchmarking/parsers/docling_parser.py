"""
Docling parser (IBM).

Converts PDF, DOCX, PPTX, HTML → Markdown via Docling's DocumentConverter.
Install: pip install docling
"""

from pathlib import Path
from .base_parser import BaseParser


class DoclingParser(BaseParser):
    name = "Docling"

    SUPPORTED = {".pdf", ".docx", ".pptx", ".html", ".htm"}

    def __init__(self):
        from docling.document_converter import DocumentConverter  # deferred import
        self._converter = DocumentConverter()

    def supports(self, path: Path) -> bool:
        return Path(path).suffix.lower() in self.SUPPORTED

    def _parse(self, path: Path) -> str:
        result = self._converter.convert(str(path))
        return result.document.export_to_markdown()
