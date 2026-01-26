"""
Abstract interfaces for the LLM Resume Parser.

Defines contracts following the Dependency Inversion Principle.
"""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Optional, List

from src.llm_based.core.models import (
    ResumeDocument,
    ExtractedResume,
    LLMRequest,
    LLMResponse,
    ParserResult,
)


class IDocumentReader(ABC):
    """Interface for reading resume documents."""

    @abstractmethod
    def read_document(self, file_path: Path) -> ResumeDocument:
        """
        Read a document and return its metadata.

        Args:
            file_path: Path to the document file

        Returns:
            ResumeDocument with metadata

        Raises:
            DocumentReadError: If document cannot be read
        """
        pass

    @abstractmethod
    def supports_format(self, file_format: str) -> bool:
        """
        Check if the reader supports a given format.

        Args:
            file_format: File format/extension

        Returns:
            True if format is supported
        """
        pass


class ITextExtractor(ABC):
    """Interface for extracting text from documents."""

    @abstractmethod
    def extract_text(self, document: ResumeDocument) -> str:
        """
        Extract raw text from a document.

        Args:
            document: The resume document

        Returns:
            Extracted text as string

        Raises:
            TextExtractionError: If text extraction fails
        """
        pass


class ILLMProvider(ABC):
    """Interface for LLM service providers."""

    @abstractmethod
    def generate(self, request: LLMRequest) -> LLMResponse:
        """
        Generate a response from the LLM.

        Args:
            request: The LLM request with prompt and context

        Returns:
            LLMResponse with generated content

        Raises:
            LLMServiceError: If LLM call fails
            LLMTimeoutError: If request times out
            LLMRateLimitError: If rate limit is exceeded
        """
        pass

    @abstractmethod
    def health_check(self) -> bool:
        """
        Check if the LLM service is healthy and accessible.

        Returns:
            True if service is healthy
        """
        pass


class ICacheService(ABC):
    """Interface for caching service."""

    @abstractmethod
    def get(self, key: str) -> Optional[str]:
        """
        Retrieve a value from cache.

        Args:
            key: Cache key

        Returns:
            Cached value or None if not found
        """
        pass

    @abstractmethod
    def set(self, key: str, value: str, ttl_seconds: Optional[int] = None) -> None:
        """
        Store a value in cache.

        Args:
            key: Cache key
            value: Value to cache
            ttl_seconds: Time to live in seconds
        """
        pass

    @abstractmethod
    def clear(self) -> None:
        """Clear all cached entries."""
        pass

    @abstractmethod
    def delete(self, key: str) -> None:
        """
        Delete a specific cache entry.

        Args:
            key: Cache key to delete
        """
        pass


class IParserService(ABC):
    """Interface for the main parser orchestration service."""

    @abstractmethod
    def parse_single(self, file_path: Path) -> ParserResult:
        """
        Parse a single resume file.

        Args:
            file_path: Path to the resume file

        Returns:
            ParserResult with extracted data or error information
        """
        pass

    @abstractmethod
    def parse_batch(self, file_paths: List[Path]) -> List[ParserResult]:
        """
        Parse multiple resume files.

        Args:
            file_paths: List of paths to resume files

        Returns:
            List of ParserResult for each file
        """
        pass


class IValidator(ABC):
    """Interface for validation operations."""

    @abstractmethod
    def validate_file(self, file_path: Path) -> bool:
        """
        Validate if a file is suitable for processing.

        Args:
            file_path: Path to the file

        Returns:
            True if file is valid

        Raises:
            ValidationError: If validation fails
        """
        pass

    @abstractmethod
    def validate_extracted_data(self, data: ExtractedResume) -> bool:
        """
        Validate extracted resume data.

        Args:
            data: Extracted resume data

        Returns:
            True if data is valid

        Raises:
            ValidationError: If validation fails
        """
        pass

