"""
Configuration settings for the LLM Resume Parser.

Uses pydantic-settings for environment-based configuration.
"""

import os
from pathlib import Path
from typing import Optional, List
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Application Settings
    app_name: str = Field(default="LLM Resume Parser", description="Application name")
    app_version: str = Field(default="2.0.0", description="Application version")
    environment: str = Field(default="development", description="Environment (development/production)")

    # LLM Provider Settings
    llm_provider: str = Field(default="huggingface", description="LLM provider name")
    llm_model_name: str = Field(
        default="google/flan-t5-large",
        description="Default LLM model name"
    )
    llm_temperature: float = Field(default=1e-10, ge=0.0, le=2.0, description="LLM temperature")
    llm_max_tokens: int = Field(default=2048, gt=0, description="Max tokens to generate")
    llm_timeout_seconds: int = Field(default=120, gt=0, description="LLM request timeout")

    # HuggingFace Settings
    huggingface_api_token: Optional[str] = Field(
        default=None,
        alias="HUGGINGFACEHUB_API_TOKEN",
        description="HuggingFace API token"
    )
    hf_api_token: Optional[str] = Field(
        default=None,
        alias="HF_API_TOKEN",
        description="Alternative HuggingFace API token"
    )
    huggingface_use_local: bool = Field(
        default=True,
        description="Use local model instead of API"
    )

    # OpenAI Settings (placeholder for future)
    openai_api_key: Optional[str] = Field(
        default=None,
        alias="OPENAI_API_KEY",
        description="OpenAI API key"
    )

    # Extraction Settings
    extraction_attributes: List[str] = Field(
        default=[
            "Name", "Email", "Phone Number", "Address", "Objective",
            "Skills", "Employment History", "Education History", "Accomplishments"
        ],
        description="Attributes to extract from resumes"
    )

    # Retry Settings
    retry_max_attempts: int = Field(default=3, ge=0, description="Maximum retry attempts")
    retry_backoff_factor: float = Field(default=2.0, gt=0, description="Retry backoff factor")
    retry_initial_wait_seconds: float = Field(default=1.0, gt=0, description="Initial retry wait")

    # Cache Settings
    cache_enabled: bool = Field(default=True, description="Enable caching")
    cache_ttl_seconds: int = Field(default=3600, gt=0, description="Cache TTL")
    cache_backend: str = Field(default="memory", description="Cache backend (memory/redis)")
    redis_url: Optional[str] = Field(default=None, description="Redis URL for caching")

    # File Processing Settings
    max_file_size_mb: int = Field(default=10, gt=0, description="Max file size in MB")
    supported_formats: List[str] = Field(
        default=["pdf", "docx", "txt"],
        description="Supported file formats"
    )

    # Logging Settings
    log_level: str = Field(default="INFO", description="Logging level")
    log_format: str = Field(
        default="json",
        description="Log format (json/text)"
    )
    log_file_path: Optional[Path] = Field(
        default=None,
        description="Path to log file"
    )
    log_rotation_size_mb: int = Field(
        default=10,
        gt=0,
        description="Log file rotation size"
    )

    # Paths
    data_folder: Path = Field(
        default_factory=lambda: Path(__file__).parent.parent.parent / "data",
        description="Default data folder path"
    )
    logs_folder: Path = Field(
        default_factory=lambda: Path(__file__).parent.parent.parent / "logs",
        description="Logs folder path"
    )
    prompts_file: Path = Field(
        default_factory=lambda: Path(__file__).parent / "prompts.yaml",
        description="Path to prompts configuration file"
    )

    def get_hf_token(self) -> Optional[str]:
        """Get HuggingFace token from available sources."""
        return (
            self.huggingface_api_token
            or self.hf_api_token
            or os.environ.get("HUGGINGFACEHUB_API_TOKEN")
            or os.environ.get("HF_API_TOKEN")
        )

    def ensure_directories(self) -> None:
        """Ensure necessary directories exist."""
        if self.logs_folder:
            self.logs_folder.mkdir(parents=True, exist_ok=True)
        if self.data_folder:
            self.data_folder.mkdir(parents=True, exist_ok=True)

    def is_production(self) -> bool:
        """Check if running in production environment."""
        return self.environment.lower() == "production"


# Global settings instance
settings = Settings()

# Ensure directories exist on import
settings.ensure_directories()

