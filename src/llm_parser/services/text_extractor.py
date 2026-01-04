"""
Text extraction service for extracting text from various document formats.

Delegates to format-specific extractors.
"""

from pathlib import Path
from typing import Dict, Type

from ..core.interfaces import ITextExtractor
from ..core.models import ResumeDocument, FileFormat
from ..core.exceptions import TextExtractionError
from ..utils.logger import get_logger
from ..utils.validators import TextValidator

logger = get_logger(__name__)


class BaseTextExtractor(ITextExtractor):
    """Base text extractor with common functionality."""

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
        raise NotImplementedError("Subclasses must implement extract_text")

    def _post_process_text(self, text: str) -> str:
        """
        Post-process extracted text.

        Args:
            text: Raw extracted text

        Returns:
            Cleaned text
        """
        if not text:
            return ""

        # Sanitize text
        text = TextValidator.sanitize_text(text)

        return text


class TextExtractorService(ITextExtractor):
    """Main text extraction service that delegates to format-specific extractors."""

    def __init__(self):
        """Initialize text extractor service."""
        self._extractors: Dict[FileFormat, ITextExtractor] = {}
        logger.info("Initialized text extractor service")

    def register_extractor(self, file_format: FileFormat, extractor: ITextExtractor) -> None:
        """
        Register an extractor for a specific format.

        Args:
            file_format: File format enum
            extractor: Text extractor instance
        """
        self._extractors[file_format] = extractor
        logger.debug(f"Registered text extractor for {file_format.value}")

    def extract_text(self, document: ResumeDocument) -> str:
        """
        Extract text from a document using the appropriate extractor.

        Args:
            document: The resume document

        Returns:
            Extracted text as string

        Raises:
            TextExtractionError: If text extraction fails
        """
        try:
            # Get appropriate extractor
            extractor = self._get_extractor(document.file_format)

            # Extract text
            logger.info(f"Extracting text from {document.filename}", format=document.file_format.value)
            text = extractor.extract_text(document)

            # Validate extracted text
            TextValidator.validate_resume_text(text)

            logger.info(
                f"Text extracted successfully from {document.filename}",
                text_length=len(text),
                format=document.file_format.value
            )

            return text

        except Exception as e:
            raise TextExtractionError(
                f"Failed to extract text from {document.filename}: {e}",
                details={
                    "filename": document.filename,
                    "format": document.file_format.value,
                    "error": str(e)
                }
            ) from e

    def _get_extractor(self, file_format: FileFormat) -> ITextExtractor:
        """
        Get the appropriate extractor for a file format.

        Args:
            file_format: File format enum

        Returns:
            ITextExtractor instance

        Raises:
            TextExtractionError: If no extractor available
        """
        if file_format not in self._extractors:
            raise TextExtractionError(
                f"No text extractor registered for format: {file_format.value}",
                details={"format": file_format.value}
            )

        return self._extractors[file_format]

    def supports_format(self, file_format: FileFormat) -> bool:
        """
        Check if a format is supported.

        Args:
            file_format: File format to check

        Returns:
            True if format is supported
        """
        return file_format in self._extractors

