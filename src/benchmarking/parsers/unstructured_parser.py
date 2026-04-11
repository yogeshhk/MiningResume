"""
Unstructured parser (Unstructured-IO).

Uses format-specific partition functions to avoid the heavy auto-detection
import chain that requires poppler/detectron2 on PATH.

Supported formats: .pdf, .docx, .txt
Install: pip install unstructured
  - PDF partition additionally needs pdfminer.six (auto-installed) and
    optionally poppler for image-based PDFs.
"""

from pathlib import Path
from .base_parser import BaseParser

_SUPPORTED = {".pdf", ".docx", ".txt"}


class UnstructuredParser(BaseParser):
    name = "Unstructured"

    def __init__(self):
        # Lightweight validation — all these are in the base package
        from unstructured.partition.text import partition_text  # noqa: F401
        from unstructured.partition.docx import partition_docx  # noqa: F401

    def supports(self, path: Path) -> bool:
        return Path(path).suffix.lower() in _SUPPORTED

    def _parse(self, path: Path) -> str:
        suffix = path.suffix.lower()

        if suffix == ".txt":
            from unstructured.partition.text import partition_text
            elements = partition_text(filename=str(path))

        elif suffix == ".docx":
            from unstructured.partition.docx import partition_docx
            elements = partition_docx(filename=str(path))

        elif suffix == ".pdf":
            # pdfminer-based partition — no poppler needed for text PDFs
            from unstructured.partition.pdf import partition_pdf
            elements = partition_pdf(filename=str(path), strategy="fast")

        else:
            raise ValueError(f"Unsupported format: {suffix}")

        return "\n\n".join(str(el) for el in elements)
