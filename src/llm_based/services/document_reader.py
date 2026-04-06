"""
Document reader service for reading resume files.

Provides a factory pattern for format-specific readers.
"""

from pathlib import Path

from src.llm_based.core.interfaces import IDocumentReader
from src.llm_based.core.models import ResumeDocument, FileFormat
from src.llm_based.core.exceptions import DocumentReadError, UnsupportedFormatError
from src.llm_based.utils.logger import get_logger
from src.llm_based.utils.validators import FileValidator

logger = get_logger(__name__)


class BaseDocumentReader(IDocumentReader):
    """Base class for document readers."""

    def __init__(self, validator: FileValidator = None):
        """
        Initialize document reader.

        Args:
            validator: File validator instance
        """
        self.validator = validator or FileValidator()

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
        # Ensure Path object
        if not isinstance(file_path, Path):
            file_path = Path(file_path)

        # Validate file
        try:
            self.validator.validate_file(file_path)
        except Exception as e:
            raise DocumentReadError(
                f"File validation failed: {e}",
                details={"file_path": str(file_path)}
            ) from e

        # Get file metadata
        try:
            file_stat = file_path.stat()
            file_ext = file_path.suffix.lower().lstrip('.')

            document = ResumeDocument(
                file_path=file_path,
                filename=file_path.name,
                file_format=FileFormat(file_ext),
                file_size_bytes=file_stat.st_size,
            )

            logger.info(
                f"Document read successfully: {file_path.name}",
                format=file_ext,
                size_bytes=file_stat.st_size
            )

            return document

        except Exception as e:
            raise DocumentReadError(
                f"Failed to read document metadata: {e}",
                details={"file_path": str(file_path)}
            ) from e

    def supports_format(self, file_format: str) -> bool:
        """
        Check if the reader supports a given format.

        Args:
            file_format: File format/extension

        Returns:
            True if format is supported
        """
        try:
            FileFormat(file_format.lower())
            return True
        except ValueError:
            return False



