"""
Unit tests for validators.
"""

import pytest
from pathlib import Path

from src.llm_based.utils.validators import (
    FileValidator,
    ResumeDataValidator,
    TextValidator,
)
from src.llm_based.core.models import ExtractedResume
from src.llm_based.core.exceptions import ValidationError


class TestFileValidator:
    """Tests for FileValidator."""

    def test_validate_file_exists(self, tmp_path):
        """Test validation of existing file."""
        validator = FileValidator()

        # Create a test file
        test_file = tmp_path / "test.pdf"
        test_file.write_text("test content")

        # Should not raise
        assert validator.validate_file(test_file) is True

    def test_validate_file_not_exists(self):
        """Test validation of non-existent file."""
        validator = FileValidator()

        with pytest.raises(ValidationError) as exc_info:
            validator.validate_file(Path("/nonexistent/file.pdf"))

        assert "does not exist" in str(exc_info.value)

    def test_validate_file_unsupported_format(self, tmp_path):
        """Test validation of unsupported format."""
        validator = FileValidator(supported_formats=["pdf", "docx"])

        test_file = tmp_path / "test.xyz"
        test_file.write_text("test")

        with pytest.raises(ValidationError) as exc_info:
            validator.validate_file(test_file)

        assert "Unsupported file format" in str(exc_info.value)

    def test_validate_file_too_large(self, tmp_path):
        """Test validation of oversized file."""
        validator = FileValidator(max_size_mb=0.001)  # Very small limit

        test_file = tmp_path / "test.pdf"
        test_file.write_bytes(b"x" * 10000)  # 10KB file

        with pytest.raises(ValidationError) as exc_info:
            validator.validate_file(test_file)

        assert "exceeds limit" in str(exc_info.value)


class TestResumeDataValidator:
    """Tests for ResumeDataValidator."""

    def test_validate_valid_email(self):
        """Test validation of valid email."""
        validator = ResumeDataValidator()

        assert validator.validate_email("test@example.com") is True
        assert validator.validate_email("user.name@company.co.uk") is True

    def test_validate_invalid_email(self):
        """Test validation of invalid email."""
        validator = ResumeDataValidator()

        assert validator.validate_email("invalid-email") is False
        assert validator.validate_email("@example.com") is False
        assert validator.validate_email("") is False

    def test_validate_valid_phone(self):
        """Test validation of valid phone."""
        validator = ResumeDataValidator()

        assert validator.validate_phone("+1 (555) 123-4567") is True
        assert validator.validate_phone("555-123-4567") is True

    def test_validate_extracted_data_success(self, sample_extracted_resume):
        """Test validation of valid extracted data."""
        validator = ResumeDataValidator()

        # Should not raise
        assert validator.validate_extracted_data(sample_extracted_resume) is True

    def test_validate_extracted_data_no_data(self):
        """Test validation of empty extracted data."""
        validator = ResumeDataValidator()

        empty_resume = ExtractedResume(filename="test.pdf")

        with pytest.raises(ValidationError) as exc_info:
            validator.validate_extracted_data(empty_resume)

        assert "No data could be extracted" in str(exc_info.value)


class TestTextValidator:
    """Tests for TextValidator."""

    def test_validate_resume_text_success(self, sample_resume_text):
        """Test validation of valid resume text."""
        assert TextValidator.validate_resume_text(sample_resume_text) is True

    def test_validate_resume_text_empty(self):
        """Test validation of empty text."""
        with pytest.raises(ValidationError) as exc_info:
            TextValidator.validate_resume_text("")

        assert "empty" in str(exc_info.value)

    def test_validate_resume_text_too_short(self):
        """Test validation of too short text."""
        with pytest.raises(ValidationError) as exc_info:
            TextValidator.validate_resume_text("Short")

        assert "too short" in str(exc_info.value)

    def test_sanitize_text(self):
        """Test text sanitization."""
        dirty_text = "Text\x00with\nnull\tbytes  and   spaces"
        clean_text = TextValidator.sanitize_text(dirty_text)

        assert "\x00" not in clean_text
        assert "null" in clean_text
        assert clean_text.strip() == clean_text

