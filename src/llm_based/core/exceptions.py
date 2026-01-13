"""
Custom exceptions for the LLM Resume Parser.

Provides a hierarchy of exceptions for better error handling and debugging.
"""


class ParserException(Exception):
    """Base exception for all parser-related errors."""

    def __init__(self, message: str, details: dict = None):
        super().__init__(message)
        self.message = message
        self.details = details or {}

    def __str__(self):
        if self.details:
            return f"{self.message} | Details: {self.details}"
        return self.message


class DocumentReadError(ParserException):
    """Raised when a document cannot be read or accessed."""
    pass


class TextExtractionError(ParserException):
    """Raised when text extraction from a document fails."""
    pass


class LLMServiceError(ParserException):
    """Raised when LLM service interaction fails."""
    pass


class ValidationError(ParserException):
    """Raised when validation of input or output fails."""
    pass


class ConfigurationError(ParserException):
    """Raised when configuration is invalid or missing."""
    pass


class CacheError(ParserException):
    """Raised when cache operations fail."""
    pass


class UnsupportedFormatError(DocumentReadError):
    """Raised when file format is not supported."""
    pass


class LLMTimeoutError(LLMServiceError):
    """Raised when LLM request times out."""
    pass


class LLMRateLimitError(LLMServiceError):
    """Raised when LLM rate limit is exceeded."""
    pass


class RetryExhaustedError(ParserException):
    """Raised when all retry attempts are exhausted."""
    pass

