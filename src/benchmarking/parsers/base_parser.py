"""
Abstract base parser.

Each concrete parser must:
  - set a class-level `name: str`
  - implement `supports(path)` — returns True if the parser handles this file type
  - implement `_parse(path)` — returns extracted plain text / markdown

The public `parse()` method wraps `_parse()` with timing and peak-memory tracking.
"""

import time
import tracemalloc
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class ParseResult:
    parser_name: str
    file_path: str
    file_name: str
    file_format: str          # e.g. "pdf", "docx", "txt"
    success: bool
    text: str = ""
    error: str = ""
    parse_time_s: float = 0.0
    peak_memory_mb: float = 0.0


class BaseParser(ABC):
    name: str = ""            # override in every subclass

    @abstractmethod
    def supports(self, path: Path) -> bool:
        """Return True if this parser can handle the given file."""

    @abstractmethod
    def _parse(self, path: Path) -> str:
        """Extract and return text content from the file."""

    def parse(self, path: Path) -> ParseResult:
        """
        Public entry point.  Calls _parse() and records timing + peak memory.
        Never raises — errors are captured in ParseResult.error.
        """
        path = Path(path)
        result = ParseResult(
            parser_name=self.name,
            file_path=str(path),
            file_name=path.name,
            file_format=path.suffix.lstrip(".").lower(),
            success=False,
        )

        tracemalloc.start()
        t0 = time.perf_counter()
        try:
            text = self._parse(path)
            result.text = text or ""
            result.success = bool(result.text.strip())
            if not result.success and not result.error:
                result.error = "EmptyOutput: parser returned no text"
        except Exception as exc:
            result.error = f"{type(exc).__name__}: {exc}"
        finally:
            result.parse_time_s = round(time.perf_counter() - t0, 4)
            _, peak = tracemalloc.get_traced_memory()
            tracemalloc.stop()
            result.peak_memory_mb = round(peak / 1_048_576, 3)

        return result
