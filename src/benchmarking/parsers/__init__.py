"""
Parser registry — instantiates all parsers, skipping those with missing dependencies.
"""

from .docling_parser import DoclingParser
from .markitdown_parser import MarkItDownParser
from .unstructured_parser import UnstructuredParser
from .pymupdf_parser import PyMuPDFParser
from .pdfplumber_parser import PDFPlumberParser
from .docx_parser import DocxParser

_PARSER_CLASSES = [
    DoclingParser,
    MarkItDownParser,
    UnstructuredParser,
    PyMuPDFParser,
    PDFPlumberParser,
    DocxParser,
]


def get_all_parsers():
    """Instantiate all parsers; skip any whose dependencies are not installed."""
    parsers = []
    for cls in _PARSER_CLASSES:
        try:
            parsers.append(cls())
            print(f"  [OK]   {cls.__name__} loaded")
        except ImportError as exc:
            print(f"  [SKIP] {cls.__name__}: missing dependency — {exc}")
        except Exception as exc:
            print(f"  [SKIP] {cls.__name__}: init error — {exc}")
    return parsers
