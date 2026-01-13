"""
Logger utility for the llm_based package.

Provides a get_logger function for consistent logging.
"""

import logging
import sys
import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional
from logging.handlers import RotatingFileHandler

from src.llm_based.config.settings import settings


class StructuredLogger:
    """Structured logger with JSON output support."""

    def __init__(self, name: str, log_file: Optional[Path] = None):
        """
        Initialize the structured logger.

        Args:
            name: Logger name (typically module name)
            log_file: Optional path to log file
        """
        self.logger = logging.getLogger(name)
        self.logger.setLevel(getattr(logging, settings.log_level.upper(), logging.INFO))

        # Avoid duplicate handlers
        if not self.logger.handlers:
            self._setup_handlers(log_file)

    def _setup_handlers(self, log_file: Optional[Path] = None) -> None:
        """Set up console and file handlers."""
        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.DEBUG)

        if settings.log_format.lower() == "json":
            console_handler.setFormatter(JSONFormatter())
        else:
            console_handler.setFormatter(TextFormatter())

        self.logger.addHandler(console_handler)

        # File handler
        log_path = log_file or settings.log_file_path
        if log_path:
            log_path.parent.mkdir(parents=True, exist_ok=True)
            file_handler = RotatingFileHandler(
                log_path,
                maxBytes=settings.log_rotation_size_mb * 1024 * 1024,
                backupCount=5,
            )
            file_handler.setLevel(logging.DEBUG)
            file_handler.setFormatter(JSONFormatter())
            self.logger.addHandler(file_handler)

    def _log_with_context(
        self, level: int, message: str, context: Optional[Dict[str, Any]] = None
    ) -> None:
        """Log a message with optional context."""
        extra = {"context": context or {}}
        self.logger.log(level, message, extra=extra)

    def debug(self, message: str, **context) -> None:
        """Log debug message."""
        self._log_with_context(logging.DEBUG, message, context)

    def info(self, message: str, **context) -> None:
        """Log info message."""
        self._log_with_context(logging.INFO, message, context)

    def warning(self, message: str, **context) -> None:
        """Log warning message."""
        self._log_with_context(logging.WARNING, message, context)

    def error(self, message: str, **context) -> None:
        """Log error message."""
        self._log_with_context(logging.ERROR, message, context)

    def exception(self, message: str, **context) -> None:
        """Log exception with traceback."""
        extra = {"context": context}
        self.logger.exception(message, extra=extra)


class JSONFormatter(logging.Formatter):
    """JSON formatter for structured logging."""

    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON."""
        log_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }

        # Add context if available
        if hasattr(record, "context"):
            log_data["context"] = record.context

        # Add exception info if present
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)

        return json.dumps(log_data)


class TextFormatter(logging.Formatter):
    """Human-readable text formatter."""

    def __init__(self):
        super().__init__(
            fmt="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )


def get_logger(name: str, log_file: Optional[Path] = None) -> StructuredLogger:
    """
    Get a structured logger instance.

    Args:
        name: Logger name (typically __name__)
        log_file: Optional path to log file

    Returns:
        StructuredLogger instance
    """
    return StructuredLogger(name, log_file)


# Module-level logger
logger = get_logger(__name__)

