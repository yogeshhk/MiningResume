"""
Configuration settings for the LLM Resume Parser.

Uses pydantic-settings for environment-based configuration.
"""
import json
import os
from pathlib import Path
from typing import Optional, List
from pydantic import Field
from dotenv import load_dotenv

load_dotenv(override=True)

class Settings:
    """Application settings loaded from environment variables."""

    # Application Settings
    app_name: str = os.getenv("APP_NAME", "LLM Resume Parser")
    app_version: str = os.getenv("APP_VERSION", "Application version")
    environment: str = os.getenv("ENVIRONMENT", "Environment (development/production)")

    # LLM Provider Settings
    llm_provider: str = os.getenv("LLM_PROVIDER", "huggingface")
    llm_model_name: str = os.getenv("LLM_MODEL_NAME", "google/flan-t5-large")
    llm_temperature: float = float(os.getenv("LLM_TEMPERATURE", 0.7))
    llm_max_tokens: int = int(os.getenv("LLM_MAX_TOKENS", 2048))
    llm_timeout_seconds: int = int(os.getenv("LLM_TIMEOUT_SECONDS", 120))
    use_local_llm: bool = bool(os.getenv("USE_LOCAL_LLM", True))

    # HuggingFace Settings
    hf_api_token: Optional[str] = os.getenv("HF_API_TOKEN")
    open_api_key: Optional[str] = os.getenv("OPENAI_API_KEY")

    ollama_api_url: Optional[str] = os.getenv("OLLAMA_API_URL", "http://localhost:11434")
    ollama_api_key: Optional[str] = os.getenv("OLLAMA_API_KEY")

    # Extraction Settings
    extraction_attributes: List[str] = json.loads(os.getenv("EXTRACTION_ATTRIBUTES", '["Name", "Email", "Phone Number", "Address", "Objective", "Skills", "Employment History", "Education History", "Accomplishments"]'))
    extraction_attributes = [attr.lower().strip() for attr in extraction_attributes]

    # Cache Settings
    cache_enabled: bool = bool(os.getenv("CACHE_ENABLED", True))
    cache_ttl_seconds: int = int(os.getenv("CACHE_TTL_SECONDS", 3600))
    cache_backend: str = os.getenv("CACHE_BACKEND", "memory")

    # Retry Settings
    retry_max_attempts: int = int(os.getenv("RETRY_MAX_ATTEMPTS", 3))
    retry_backoff_factor: float = float(os.getenv("RETRY_BACKOFF_FACTOR", 2.0))
    retry_initial_wait_seconds: float = float(os.getenv("RETRY_INITIAL_WAIT_SECONDS", 1.0))


    # File Processing Settings
    max_file_size_mb: int = int(os.getenv("MAX_FILE_SIZE_MB", 10))
    supported_formats: List[str] = json.loads(os.getenv("SUPPORTED_FORMATS", '["pdf", "docx", "txt"]'))
    supported_formats = [fmt.lower().strip() for fmt in supported_formats]
    fail_fast_for_batch: bool = bool(os.getenv("FAIL_FAST_FOR_BATCH", True))

    # Logging Settings
    log_level: str = os.getenv("LOG_LEVEL", "INFO")
    log_format: str = os.getenv("LOG_FORMAT", "json")
    log_rotation_size_mb: int = int(os.getenv("LOG_ROTATION_SIZE_MB", 10))

    # Paths
    data_folder: Path = Path(__file__).parent.parent.parent / "data"
    logs_folder: Path = Path(__file__).parent.parent.parent / "logs"
    log_file_path: str = Path(logs_folder) / "app.log"
    prompts_file: Path = Field(
        default_factory=lambda: Path(__file__).parent / "prompts.yaml",
        description="Path to prompts configuration file"
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

