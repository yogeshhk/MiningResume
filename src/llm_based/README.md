# LLM Resume Parser v2.0 - Production-Grade Architecture

A refactored, production-ready resume parsing system using Large Language Models, following SOLID principles with comprehensive testing and observability.

## 🎯 What's New in v2.0

This is a **complete refactoring** of the LLM-based resume parser with:

- ✅ **SOLID Principles**: Clean architecture with separation of concerns
- ✅ **Modular Design**: Pluggable components via interfaces
- ✅ **Production Features**: Retry logic, caching, comprehensive logging
- ✅ **Fault Tolerance**: Graceful error handling and recovery
- ✅ **Observability**: Structured logging, metrics, and performance tracking
- ✅ **Testability**: Unit tests infrastructure
- ✅ **Type Safety**: Pydantic models for core entities
- ✅ **Multiple LLM Support**: Interface-based design for easy provider switching

## 📁 Project Structure

```
src/
└── llm_based/                     # Main package
    ├── core/                      # Core domain models and interfaces
    │   ├── models.py              # Pydantic data models
    │   ├── interfaces.py          # Abstract interfaces (SOLID - D)
    │   └── exceptions.py          # Custom exceptions
    ├── services/                  # Business logic services
    │   ├── cache_service.py       # Cache helpers (keys, optional backend)
    │   ├── document_reader.py     # Document reading orchestration
    │   ├── text_extractor.py      # Text extraction service
    │   ├── llm_service.py         # LLM interaction abstraction
    │   └── parser_service.py      # Main orchestration service
    ├── adapters/                  # External integrations
    │   ├── file_adapters.py       # PDF, DOCX, TXT readers
    │   ├── huggingface_adapter.py # HuggingFace LLM provider
    │   ├── ollama_adapter.py      # Ollama provider (optional)
    │   └── openai_adapter.py      # OpenAI provider (placeholder)
    ├── utils/                     # Utilities
    │   ├── logger.py              # Structured logging
    │   ├── validators.py          # Input/output validation
    │   ├── retry.py               # Retry with backoff
    │   └── metrics.py             # Performance metrics
    ├── config/                    # Configuration
    │   ├── settings.py            # Environment-based config
    │   └── prompts.yaml           # Prompt templates
    ├── example_usage.py           # Example script
    ├── README.md                  # Package documentation
    └── IMPLEMENTATION_SUMMARY.md  # Summary doc
```

## 🚀 Quick Start

### 1. Installation

```bash
# Install dependencies using uv (recommended)
uv pip install --system
```

### 2. Basic Usage (Python API)

```python
from pathlib import Path
from src.llm_based.services.parser_service import ParserService
from src.llm_based.services.document_reader import DocumentReaderFactory
from src.llm_based.services.text_extractor import TextExtractorService
from src.llm_based.services.llm_service import LLMService
from src.llm_based.adapters.huggingface_adapter import HuggingFaceAdapter

# Setup dependencies
reader = DocumentReaderFactory._default_reader
text_extractor = TextExtractorService()
provider = HuggingFaceAdapter()  # Uses settings.use_local_llm and settings.llm_model_name
llm_service = LLMService(provider=provider)
parser = ParserService(document_reader=reader, text_extractor=text_extractor, llm_service=llm_service)

# Parse a single file
result = parser.parse_single(Path("data/resume.pdf"))

if result.success and result.extracted_data:
    print(result.extracted_data.to_json(indent=2))
else:
    print("Error:", result.error_message)
```

## 🛠️ End-to-End Example

For a complete, runnable setup, see `src/llm_based/example_usage.py`. It shows:
- Creating the DocumentReader, TextExtractorService, and HuggingFaceAdapter
- Wiring the LLMService and ParserService together
- Parsing a file under `data/` and printing structured output

Open `example_usage.py` and run the script after configuring environment variables to quickly validate your setup.

## 🏗️ Architecture Highlights

### SOLID Principles Applied

1. **Single Responsibility**: Each class has one reason to change
   - `DocumentReader` only reads files
   - `TextExtractorService` delegates extraction
   - `LLMService` handles prompts, caching, retry, metrics

2. **Open/Closed**: Open for extension, closed for modification
   - New LLM providers via `ILLMProvider` interface
   - New file formats via `ITextExtractor` interface

3. **Liskov Substitution**: Interfaces are interchangeable
   - Any `ILLMProvider` can replace another
   - Any `ITextExtractor` can replace another

4. **Interface Segregation**: Focused interfaces
   - Small, specific interfaces
   - Clients depend only on methods they use

5. **Dependency Inversion**: Depend on abstractions
   - Services depend on interfaces, not implementations
   - Dependency injection throughout

### Key Features

#### 1. Retry Logic with Exponential Backoff

```python
from src.llm_based.utils.retry import retry_with_backoff

@retry_with_backoff(max_attempts=3, initial_wait=1.0, backoff_factor=2.0)
def _generate_with_retry(self, request):
    # Automatic retry on LLMServiceError or LLMTimeoutError
    pass
```

#### 2. Caching

```python
# LLMService supports optional cache injection and uses CacheKeyGenerator
# TTL controlled via settings.cache_ttl_seconds
```

#### 3. Structured Logging

```python
from src.llm_based.utils.logger import get_logger
logger = get_logger(__name__)

logger.info(
    "Processing resume",
    filename=document.filename,
    size_bytes=document.file_size_bytes
)
```

#### 4. Validation

```python
# File validation
# validators.FileValidator is used in DocumentReader

# Data validation
# validators.ResumeDataValidator validates ExtractedResume

# Text validation
# validators.TextValidator sanitizes and validates resume text
```

#### 5. Metrics & Observability

```python
# Performance timing via PerformanceTimer
# Token usage tracking via TokenCounter
# Metrics aggregation via get_metrics_collector
```

## 🔌 Pluggable LLM Providers

The architecture supports multiple LLM providers via the `ILLMProvider` interface:

### Current: HuggingFace (Default)

```python
from src.llm_based.adapters.huggingface_adapter import HuggingFaceAdapter
provider = HuggingFaceAdapter()  # Configured via settings
```

### Optional: Ollama

```python
from src.llm_based.adapters.ollama_adapter import OllamaAdapter
# Configure via settings.OLLAMA_* if used
```

### Future: OpenAI (Placeholder)

```python
from src.llm_based.adapters.openai_adapter import OpenAIAdapter
# Placeholder adapter; not wired into LLMService yet
```

### Custom Provider

```python
from src.llm_based.core.interfaces import ILLMProvider

class CustomLLMAdapter(ILLMProvider):
    def generate(self, request):
        # Your implementation
        ...
    def health_check(self) -> bool:
        ...
```

## 🧪 Testing

```bash
# Run all tests
pytest

# Run specific tests (examples)
pytest -k unit
pytest -v
```

## 📊 Configuration

### Environment Variables (.env)

```bash
# LLM Settings
LLM_PROVIDER="huggingface"
LLM_MODEL_NAME="google/flan-t5-large"
LLM_TEMPERATURE=0.7
LLM_MAX_TOKENS=2048
LLM_TIMEOUT_SECONDS=120
USE_LOCAL_LLM=true

# HuggingFace
HF_API_TOKEN="your_token_here"

# Cache
CACHE_ENABLED=true
CACHE_TTL_SECONDS=3600

# Retry
RETRY_MAX_ATTEMPTS=3
RETRY_BACKOFF_FACTOR=2.0
RETRY_INITIAL_WAIT_SECONDS=1.0

# Logging
LOG_LEVEL="INFO"
LOG_FORMAT="json"
```

### Prompt Templates (config/prompts.yaml)

```yaml
extraction:
  user_prompt_template: |
    Extract {attribute} from the following resume text.

    Resume:
    {resume}

    Extracted {attribute}:
```

## 🔍 Observability

### Logging Levels

- **DEBUG**: Detailed diagnostic information
- **INFO**: General informational messages
- **WARNING**: Warning messages (non-critical)
- **ERROR**: Error messages with context

### Metrics Tracked (examples)

- Processing time per file
- LLM call count
- Cache hits
- Token usage

## 🔧 Error Handling

### Custom Exceptions

- `DocumentReadError`: File reading failures
- `TextExtractionError`: Text extraction failures
- `LLMServiceError`: LLM interaction failures
- `LLMTimeoutError`: Request timeouts
- `ValidationError`: Data validation failures
- `UnsupportedFormatError`: Unsupported file formats
- `RetryExhaustedError`: All retry attempts failed

### Graceful Degradation

- Partial results on attribute extraction failure
- Configurable fail-fast for batch processing

## 📈 Performance

### Caching

- Reduces redundant LLM calls when enabled
- TTL configurable via settings

### Batch Processing

- Process multiple files efficiently
- Shared configuration across batch

## 🛣️ Migration from v1.0

The old `llm_resume_parser.py` remains untouched. To migrate:

1. Review the new architecture in `src/llm_based/`
2. Use `example_usage.py` as a reference
3. Update imports to new package structure
4. Configure via environment variables (settings.py reads them)

## 🤝 Contributing

1. Follow SOLID principles
2. Write unit tests for new features
3. Use type hints throughout
4. Document with docstrings
5. Log important operations

## 📝 License

Copyright (C) 2026 Yogesh H Kulkarni

## 🔮 Future Enhancements

- [ ] Async/await support for concurrent processing
- [ ] OpenAI adapter implementation
- [ ] Redis cache backend
- [ ] API server (FastAPI/Flask)
- [ ] Knowledge Graph integration
- [ ] Chatbot interface
- [ ] Docker containerization
- [ ] CI/CD pipeline

---

**Note**: This is v2.0 - a production-grade refactoring. For the original simple version, see `llm_resume_parser.py`.

## Dependency Management Update

- Dependencies can be managed using uv and the environment's package manager.
- Use `uv pip install --system` to install all packages in your environment.
- This helps ensure consistent environments for development, CI/CD, and deployment.
