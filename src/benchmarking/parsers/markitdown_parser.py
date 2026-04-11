"""
MarkItDown parser (Microsoft).

Converts PDF, DOCX, XLSX, PPTX, HTML → Markdown.
Install: pip install markitdown
"""

from pathlib import Path
from .base_parser import BaseParser


class MarkItDownParser(BaseParser):
    name = "MarkItDown"

    SUPPORTED = {".pdf", ".docx", ".xlsx", ".pptx", ".html", ".htm", ".txt"}

    def __init__(self):
        from markitdown import MarkItDown  # deferred import
        self._converter = MarkItDown(enable_plugins=False)

    def supports(self, path: Path) -> bool:
        return Path(path).suffix.lower() in self.SUPPORTED

    def _parse(self, path: Path) -> str:
        result = self._converter.convert(str(path))
        return result.text_content or ""
