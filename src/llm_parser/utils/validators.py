"""
Validation utilities for input and output data.

Provides validators for files, resume text, and extracted data.
"""

import re
from pathlib import Path
from typing import List, Optional

from ..core.models import ResumeDocument, ExtractedResume, FileFormat
from ..core.exceptions import ValidationError
from ..core.interfaces import IValidator
from ..config.settings import settings
from ..utils.logger import get_logger

logger = get_logger(__name__)


class FileValidator(IValidator):
    """Validator for file operations."""

    def __init__(self, max_size_mb: Optional[int] = None, supported_formats: Optional[List[str]] = None):
        """
        Initialize file validator.

        Args:
            max_size_mb: Maximum file size in MB
            supported_formats: List of supported file formats
        """
        self.max_size_mb = max_size_mb or settings.max_file_size_mb
        self.supported_formats = supported_formats or settings.supported_formats

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
        # Check if file exists
        if not file_path.exists():
            raise ValidationError(
                f"File does not exist: {file_path}",
                details={"file_path": str(file_path)}
            )

        # Check if it's a file
        if not file_path.is_file():
            raise ValidationError(
                f"Path is not a file: {file_path}",
                details={"file_path": str(file_path)}
            )

        # Check file format
        file_ext = file_path.suffix.lower().lstrip('.')
        if file_ext not in self.supported_formats:
            raise ValidationError(
                f"Unsupported file format: {file_ext}",
                details={
                    "file_path": str(file_path),
                    "format": file_ext,
                    "supported_formats": self.supported_formats
                }
            )

        # Check file size
        file_size_mb = file_path.stat().st_size / (1024 * 1024)
        if file_size_mb > self.max_size_mb:
            raise ValidationError(
                f"File size exceeds limit: {file_size_mb:.2f}MB > {self.max_size_mb}MB",
                details={
                    "file_path": str(file_path),
                    "file_size_mb": file_size_mb,
                    "max_size_mb": self.max_size_mb
                }
            )

        logger.debug(
            f"File validation passed: {file_path.name}",
            file_size_mb=f"{file_size_mb:.2f}",
            format=file_ext
        )
        return True

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
        # This method is required by IValidator interface
        # Actual validation is delegated to ResumeDataValidator
        validator = ResumeDataValidator()
        return validator.validate_extracted_data(data)


class ResumeDataValidator(IValidator):
    """Validator for extracted resume data."""

    EMAIL_PATTERN = re.compile(
        r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    )

    PHONE_PATTERN = re.compile(
        r'^\+?[\d\s\-()]{7,}$'
    )

    def validate_file(self, file_path: Path) -> bool:
        """Not applicable for data validator."""
        return True

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
        errors = []
        warnings = []

        # Validate email if present
        if data.email and data.email.strip():
            if not self.EMAIL_PATTERN.match(data.email.strip()):
                warnings.append(f"Email format may be invalid: {data.email}")

        # Validate phone if present
        if data.phone_number and data.phone_number.strip():
            if not self.PHONE_PATTERN.match(data.phone_number.strip()):
                warnings.append(f"Phone format may be invalid: {data.phone_number}")

        # Check if at least some data was extracted
        non_empty_fields = sum(
            1 for field in [
                data.name, data.email, data.phone_number, data.address,
                data.objective, data.skills, data.employment_history,
                data.education_history, data.accomplishments
            ] if field and field.strip()
        )

        if non_empty_fields == 0:
            errors.append("No data could be extracted from the resume")
        elif non_empty_fields < 3:
            warnings.append(
                f"Only {non_empty_fields} fields extracted - resume may be incomplete or poorly formatted"
            )

        # Log warnings
        for warning in warnings:
            logger.warning(warning, filename=data.filename)

        # Raise error if critical validation failed
        if errors:
            raise ValidationError(
                "Resume data validation failed",
                details={
                    "filename": data.filename,
                    "errors": errors,
                    "warnings": warnings
                }
            )

        logger.debug(
            f"Data validation passed: {data.filename}",
            non_empty_fields=non_empty_fields,
            warnings_count=len(warnings)
        )
        return True

    def validate_email(self, email: str) -> bool:
        """
        Validate email format.

        Args:
            email: Email address to validate

        Returns:
            True if valid
        """
        if not email or not email.strip():
            return False
        return bool(self.EMAIL_PATTERN.match(email.strip()))

    def validate_phone(self, phone: str) -> bool:
        """
        Validate phone number format.

        Args:
            phone: Phone number to validate

        Returns:
            True if valid
        """
        if not phone or not phone.strip():
            return False
        return bool(self.PHONE_PATTERN.match(phone.strip()))


class TextValidator:
    """Validator for text content."""

    MIN_TEXT_LENGTH = 50  # Minimum characters for a valid resume

    @staticmethod
    def validate_resume_text(text: str) -> bool:
        """
        Validate resume text content.

        Args:
            text: Resume text to validate

        Returns:
            True if text is valid

        Raises:
            ValidationError: If validation fails
        """
        if not text or not text.strip():
            raise ValidationError(
                "Resume text is empty",
                details={"text_length": 0}
            )

        text_length = len(text.strip())
        if text_length < TextValidator.MIN_TEXT_LENGTH:
            raise ValidationError(
                f"Resume text too short: {text_length} < {TextValidator.MIN_TEXT_LENGTH}",
                details={
                    "text_length": text_length,
                    "min_length": TextValidator.MIN_TEXT_LENGTH
                }
            )

        logger.debug(
            "Resume text validation passed",
            text_length=text_length
        )
        return True

    @staticmethod
    def sanitize_text(text: str) -> str:
        """
        Sanitize text by removing problematic characters.

        Args:
            text: Text to sanitize

        Returns:
            Sanitized text
        """
        if not text:
            return ""

        # Remove null bytes
        text = text.replace('\x00', '')

        # Normalize whitespace
        text = re.sub(r'\s+', ' ', text)

        # Remove control characters except newlines and tabs
        text = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]', '', text)

        return text.strip()

