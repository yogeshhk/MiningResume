"""
Core data models for the LLM Resume Parser.

Uses Pydantic for data validation and serialization.
"""

from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, field_validator, ConfigDict


class FileFormat(str, Enum):
    """Supported file formats for resume documents."""
    PDF = "pdf"
    DOCX = "docx"
    TXT = "txt"


class ResumeDocument(BaseModel):
    """Represents a resume document with metadata."""

    model_config = ConfigDict(arbitrary_types_allowed=True)

    file_path: Path = Field(..., description="Path to the resume file")
    filename: str = Field(..., description="Name of the file")
    file_format: FileFormat = Field(..., description="Format of the file")
    file_size_bytes: int = Field(..., description="Size of file in bytes")
    created_at: datetime = Field(default_factory=datetime.now)

    @field_validator("file_path")
    @classmethod
    def validate_file_exists(cls, path: Path) -> Path:
        """Validate that the file exists."""
        if not path.exists():
            raise ValueError(f"File does not exist: {path}")
        if not path.is_file():
            raise ValueError(f"Path is not a file: {path}")
        return path

    @field_validator("file_format", mode="before")
    @classmethod
    def validate_format(cls, file_format: Any, info) -> FileFormat:
        """Validate and normalize file format."""
        if isinstance(file_format, FileFormat):
            return file_format
        if isinstance(file_format, str):
            # Try to get from file extension if not provided
            if hasattr(info, 'data') and 'file_path' in info.data:
                ext = Path(info.data['file_path']).suffix.lower().lstrip('.')
                try:
                    return FileFormat(ext)
                except ValueError:
                    pass
            try:
                return FileFormat(file_format.lower())
            except ValueError:
                raise ValueError(f"Unsupported file format: {file_format}")
        raise ValueError(f"Invalid format type: {type(file_format)}")


class ExtractedResume(BaseModel):
    """Represents extracted resume data with dynamic attributes."""

    model_config = ConfigDict(arbitrary_types_allowed=True, extra='allow')

    filename: str = Field(..., description="Source filename")
    attributes: Dict[str, Optional[str]] = Field(default_factory=dict, description="Dynamically extracted attributes")
    extraction_timestamp: datetime = Field(default_factory=datetime.now)
    extraction_metadata: Dict[str, Any] = Field(default_factory=dict)

    def __getitem__(self, attribute_name: str) -> Optional[str]:
        return self.fields.get(attribute_name)

    def __setitem__(self, attribute_name, attribute_value: Optional[str]) -> None:
        self.fields[attribute_name] = attribute_value

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary with all fields."""
        base = {
            "filename": self.filename,
            **self.fields,
            "extraction_timestamp": self.extraction_timestamp.isoformat(),
            "extraction_metadata": self.extraction_metadata,
        }
        return base

    def to_json(self, **kwargs) -> str:
        """Serialize to JSON string."""
        import json
        return json.dumps(self.to_dict(), **kwargs)


class LLMRequest(BaseModel):
    """Request model for LLM interactions."""

    prompt: str = Field(..., description="The prompt to send to the LLM")
    context: str = Field(..., description="The context (resume text)")
    attribute: str = Field(..., description="The attribute being extracted")
    max_tokens: Optional[int] = Field(None, description="Maximum tokens to generate")
    temperature: Optional[float] = Field(None, description="Sampling temperature")

    model_config = ConfigDict(extra='forbid')


class LLMResponse(BaseModel):
    """Response model from LLM interactions."""

    content: str = Field(..., description="The generated content")
    attribute: str = Field(..., description="The attribute that was extracted")
    tokens_used: Optional[int] = Field(None, description="Number of tokens used")
    latency_ms: Optional[float] = Field(None, description="Response latency in milliseconds")
    model_name: Optional[str] = Field(None, description="Name of the model used")
    cached: bool = Field(False, description="Whether response was from cache")

    model_config = ConfigDict(extra='allow')


class ParserConfig(BaseModel):
    """Configuration for the parser behavior."""

    # LLM Configuration
    model_name: str = Field(default="google/flan-t5-large", description="LLM model name")
    temperature: float = Field(default=1e-10, ge=0.0, le=2.0, description="Sampling temperature")
    max_tokens: int = Field(default=2048, gt=0, description="Maximum tokens to generate")
    timeout_seconds: int = Field(default=120, gt=0, description="Request timeout in seconds")

    # Extraction Configuration
    attributes_to_extract: List[str] = Field(
        default=[
            "Name", "Email", "Phone Number", "Address", "Objective",
            "Skills", "Employment History", "Education History", "Accomplishments"
        ],
        description="List of attributes to extract from resumes"
    )

    # Retry Configuration
    max_retries: int = Field(default=3, ge=0, description="Maximum retry attempts")
    retry_backoff_factor: float = Field(default=2.0, gt=0, description="Exponential backoff factor")
    retry_initial_wait: float = Field(default=1.0, gt=0, description="Initial wait time in seconds")

    # Cache Configuration
    cache_enabled: bool = Field(default=True, description="Enable response caching")
    cache_ttl_seconds: int = Field(default=3600, gt=0, description="Cache TTL in seconds")

    # File Configuration
    max_file_size_mb: int = Field(default=10, gt=0, description="Maximum file size in MB")

    # Processing Configuration
    batch_size: int = Field(default=5, gt=0, description="Batch size for processing multiple files")
    fail_fast: bool = Field(default=False, description="Stop on first error")

    model_config = ConfigDict(extra='forbid', validate_assignment=True)


class ParserResult(BaseModel):
    """Result of a parsing operation with metadata."""

    success: bool = Field(..., description="Whether parsing was successful")
    extracted_data: Optional[ExtractedResume] = Field(None, description="Extracted resume data")
    error_message: Optional[str] = Field(None, description="Error message if failed")
    error_details: Optional[Dict[str, Any]] = Field(None, description="Additional error details")
    processing_time_seconds: float = Field(..., description="Total processing time")
    llm_calls_count: int = Field(default=0, description="Number of LLM calls made")
    cache_hits_count: int = Field(default=0, description="Number of cache hits")

    model_config = ConfigDict(extra='allow')

