"""
File adapters for reading different document formats.

Implements format-specific text extraction logic.
"""

import PyPDF2
import docx2txt
from pathlib import Path
from typing import Optional

from ..core.models import ResumeDocument, FileFormat
from ..core.exceptions import TextExtractionError
from ..services.text_extractor import BaseTextExtractor
from ..utils.logger import get_logger

logger = get_logger(__name__)


class PDFTextExtractor(BaseTextExtractor):
    """Text extractor for PDF files."""

    def extract_text(self, document: ResumeDocument) -> str:
        """
        Extract text from a PDF file.

        Args:
            document: The resume document

        Returns:
            Extracted text as string

        Raises:
            TextExtractionError: If text extraction fails
        """
        try:
            logger.debug(f"Extracting text from PDF: {document.filename}")

            raw_text = ""
            with open(document.file_path, "rb") as pdf_file:
                pdf_reader = PyPDF2.PdfReader(pdf_file)

                num_pages = len(pdf_reader.pages)
                logger.debug(f"PDF has {num_pages} pages", file=document.filename)

                for page_num, page in enumerate(pdf_reader.pages, 1):
                    try:
                        page_text = page.extract_text()
                        if page_text:
                            raw_text += page_text
                            logger.debug(
                                f"Extracted text from page {page_num}",
                                file=document.filename,
                                text_length=len(page_text)
                            )
                    except Exception as e:
                        logger.warning(
                            f"Failed to extract text from page {page_num}: {e}",
                            file=document.filename
                        )

            # Post-process
            text = self._post_process_text(raw_text)

            logger.info(
                f"PDF text extraction complete: {document.filename}",
                total_length=len(text)
            )

            return text

        except Exception as e:
            raise TextExtractionError(
                f"Failed to extract text from PDF: {e}",
                details={
                    "filename": document.filename,
                    "file_path": str(document.file_path),
                }
            ) from e


class DOCXTextExtractor(BaseTextExtractor):
    """Text extractor for DOCX files."""

    def extract_text(self, document: ResumeDocument) -> str:
        """
        Extract text from a DOCX file.

        Args:
            document: The resume document

        Returns:
            Extracted text as string

        Raises:
            TextExtractionError: If text extraction fails
        """
        try:
            logger.debug(f"Extracting text from DOCX: {document.filename}")

            raw_text = docx2txt.process(str(document.file_path))

            # Post-process
            text = self._post_process_text(raw_text)

            logger.info(
                f"DOCX text extraction complete: {document.filename}",
                total_length=len(text)
            )

            return text

        except Exception as e:
            raise TextExtractionError(
                f"Failed to extract text from DOCX: {e}",
                details={
                    "filename": document.filename,
                    "file_path": str(document.file_path),
                }
            ) from e


class TXTTextExtractor(BaseTextExtractor):
    """Text extractor for plain text files."""

    def __init__(self, encoding: str = "utf-8"):
        """
        Initialize TXT extractor.

        Args:
            encoding: Text file encoding
        """
        super().__init__()
        self.encoding = encoding

    def extract_text(self, document: ResumeDocument) -> str:
        """
        Extract text from a TXT file.

        Args:
            document: The resume document

        Returns:
            Extracted text as string

        Raises:
            TextExtractionError: If text extraction fails
        """
        try:
            logger.debug(f"Extracting text from TXT: {document.filename}")

            # Try multiple encodings if needed
            encodings = [self.encoding, "utf-8", "latin-1", "cp1252"]
            raw_text = None
            used_encoding = None

            for enc in encodings:
                try:
                    with open(document.file_path, 'r', encoding=enc) as file:
                        raw_text = file.read()
                        used_encoding = enc
                        break
                except UnicodeDecodeError:
                    continue

            if raw_text is None:
                raise TextExtractionError(
                    f"Failed to decode text file with any encoding: {encodings}",
                    details={"filename": document.filename}
                )

            # Post-process
            text = self._post_process_text(raw_text)

            logger.info(
                f"TXT text extraction complete: {document.filename}",
                encoding=used_encoding,
                total_length=len(text)
            )

            return text

        except TextExtractionError:
            raise
        except Exception as e:
            raise TextExtractionError(
                f"Failed to extract text from TXT: {e}",
                details={
                    "filename": document.filename,
                    "file_path": str(document.file_path),
                }
            ) from e


def create_text_extractor_for_format(file_format: FileFormat) -> BaseTextExtractor:
    """
    Factory function to create appropriate text extractor.

    Args:
        file_format: File format enum

    Returns:
        BaseTextExtractor implementation

    Raises:
        ValueError: If format is not supported
    """
    extractors = {
        FileFormat.PDF: PDFTextExtractor,
        FileFormat.DOCX: DOCXTextExtractor,
        FileFormat.TXT: TXTTextExtractor,
    }

    extractor_class = extractors.get(file_format)
    if not extractor_class:
        raise ValueError(f"No extractor available for format: {file_format.value}")

    return extractor_class()

