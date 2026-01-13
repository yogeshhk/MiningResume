"""Adapters module initialization."""

from src.llm_based.adapters.file_adapters import (
    PDFTextExtractor,
    DOCXTextExtractor,
    TXTTextExtractor,
    create_text_extractor_for_format,
)
from src.llm_based.adapters.huggingface_adapter import HuggingFaceAdapter
from src.llm_based.adapters.openai_adapter import OpenAIAdapter

# __all__ defines the public API of this module. Only the names listed here
# will be imported when using 'from adapters import *'.
__all__ = [
    # File Adapters
    "PDFTextExtractor",
    "DOCXTextExtractor",
    "TXTTextExtractor",
    "create_text_extractor_for_format",
    # LLM Adapters
    "HuggingFaceAdapter",
    "OpenAIAdapter",
]
