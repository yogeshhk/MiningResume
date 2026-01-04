"""
Document reader service for reading resume files.

Provides a factory pattern for format-specific readers.
"""

from pathlib import Path
from typing import Dict, Type

from ..core.interfaces import IDocumentReader
from ..core.models import ResumeDocument, FileFormat
from ..core.exceptions import DocumentReadError, UnsupportedFormatError
from ..utils.logger import get_logger
from ..utils.validators import FileValidator

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


class DocumentReaderFactory:
    """Factory for creating appropriate document readers."""

    _readers: Dict[FileFormat, Type[IDocumentReader]] = {}
    _default_reader: IDocumentReader = None

    @classmethod
    def register_reader(cls, file_format: FileFormat, reader_class: Type[IDocumentReader]) -> None:
        """
        Register a reader for a specific format.

        Args:
            file_format: File format enum
            reader_class: Reader class to register
        """
        cls._readers[file_format] = reader_class
        logger.debug(f"Registered reader for {file_format.value}", reader_class=reader_class.__name__)

    @classmethod
    def get_reader(cls, file_format: FileFormat) -> IDocumentReader:
        """
        Get a reader for the specified format.

        Args:
            file_format: File format enum

        Returns:
            IDocumentReader instance

        Raises:
            UnsupportedFormatError: If format is not supported
        """
        if file_format in cls._readers:
            reader_class = cls._readers[file_format]
            return reader_class()

        # Fallback to default reader
        if cls._default_reader is None:
            cls._default_reader = BaseDocumentReader()

        if cls._default_reader.supports_format(file_format.value):
            return cls._default_reader

        raise UnsupportedFormatError(
            f"No reader available for format: {file_format.value}",
            details={"format": file_format.value}
        )

    @classmethod
    def create_reader_for_file(cls, file_path: Path) -> IDocumentReader:
        """
        Create an appropriate reader based on file extension.

        Args:
            file_path: Path to the file

        Returns:
            IDocumentReader instance

        Raises:
            UnsupportedFormatError: If format is not supported
        """
        if not isinstance(file_path, Path):
            file_path = Path(file_path)

        file_ext = file_path.suffix.lower().lstrip('.')

        try:
            file_format = FileFormat(file_ext)
            return cls.get_reader(file_format)
        except ValueError:
            raise UnsupportedFormatError(
                f"Unsupported file format: {file_ext}",
                details={"file_path": str(file_path), "extension": file_ext}
            )


# Initialize default reader
DocumentReaderFactory._default_reader = BaseDocumentReader()

