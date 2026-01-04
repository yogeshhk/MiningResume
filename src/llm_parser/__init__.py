"""
LLM-based Resume Parser Package

A production-grade resume parsing system using Large Language Models.
Follows SOLID principles with modular, testable, and fault-tolerant design.
"""

__version__ = "2.0.0"
__author__ = "Yogesh H Kulkarni"

from .core.models import ResumeDocument, ExtractedResume, ParserConfig
from .core.exceptions import (
    ParserException,
    DocumentReadError,
    TextExtractionError,
    LLMServiceError,
)

__all__ = [
    "ResumeDocument",
    "ExtractedResume",
    "ParserConfig",
    "ParserException",
    "DocumentReadError",
    "TextExtractionError",
    "LLMServiceError",
]

