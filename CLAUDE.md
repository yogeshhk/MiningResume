# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

MiningResume is a resume parsing library with three engines and a benchmarking module:
- **LLM-based** (`src/llm_based/`): Production-grade v2.0 with SOLID principles, pluggable LLM providers (HuggingFace, Ollama, OpenAI placeholder), caching, retry, and observability.
- **Rule-based** (`src/rule_based/`): Regex extraction driven by an XML config file.
- **Knowledge base** (`src/knowledge_base/`): Nascent Neo4j-based graph components.
- **Benchmarking** (`src/benchmarking/`): Compares six open-source document-parsing libraries across all resume files in `data/`, producing a CSV + HTML report.

The mode is selected via the `MODE` constant at the top of `src/main.py`.

## Setup & Dependencies

The LLM-based engine uses `uv` for dependency management with its own `pyproject.toml`:

```bash
# Install dependencies (from src/llm_based/)
cd src/llm_based
uv sync

# Or with pip
pip install -e src/llm_based
```

Copy and configure the environment file before running:
```bash
cp src/.env.example src/.env
# Edit src/.env — set LLM_PROVIDER (huggingface/ollama/openai), model name, and API tokens
```

Key env vars: `LLM_PROVIDER`, `LLM_MODEL_NAME`, `USE_LOCAL_LLM`, `OLLAMA_API_URL`, `HF_API_TOKEN`, `EXTRACTION_ATTRIBUTES`.

## Running

```bash
# Run with mode set in src/main.py (MODE = "llm" or "rule")
python -m src.main

# Or run the LLM example directly
python src/llm_based/example_usage.py
```

The default input file is `data/YogeshKulkarniLinkedInProfile.pdf`; change `FILE_PATH` in `src/main.py`.

## Testing

Tests live in `src/llm_based/tests/`. Run from `src/llm_based/`:

```bash
cd src/llm_based
pytest                          # All tests with coverage (80% threshold)
pytest tests/unit/              # Unit tests only
pytest -m "not slow"            # Skip slow tests
pytest tests/unit/test_validators.py  # Single test file
```

Coverage reports are written to HTML and printed to terminal. Markers: `unit`, `integration`, `slow`.

## Architecture (LLM-based engine)

The engine follows a layered, interface-driven design:

```
core/         → Domain models (Pydantic), abstract interfaces, custom exceptions
services/     → Business logic: DocumentReader → TextExtractorService → LLMService → ParserService
adapters/     → Plug-in implementations: file formats (PDF/DOCX/TXT), LLM providers
utils/        → Cross-cutting: structured JSON logger, retry decorator, validators, metrics
config/       → Pydantic BaseSettings (env-driven) + externalized prompts.yaml
```

**Data flow**: `ParserService` orchestrates the pipeline — `DocumentReader` validates the file path → `TextExtractorService` delegates to the appropriate `adapters/file_adapters.py` extractor → `LLMService` calls the configured `ILLMProvider` adapter with retry/cache → result returned as `ExtractedResume` Pydantic model.

**Adding a new LLM provider**: implement `ILLMProvider` from `core/interfaces.py` and wire it in `services/llm_service.py`.

**Adding a new file format**: implement `ITextExtractor` from `core/interfaces.py`, add to `adapters/file_adapters.py`, and register in `services/text_extractor.py`.

## Rule-based engine

`src/rule_based/regex_resume_parser.py` loads extraction rules from `src/rule_based/regex_config.xml` (terms, methods, patterns per field). No separate install needed beyond standard Python libraries.

## Benchmarking (`src/benchmarking/`)

Compares six open-source document parsers across all resume files in `data/`.

```bash
# Install deps (from repo root, with the active env)
pip install docling markitdown unstructured pymupdf pdfplumber python-docx

# Run benchmark (writes src/benchmarking/results/raw_results.json)
python -m src.benchmarking.benchmark_runner

# Generate CSV + HTML report
python -m src.benchmarking.report_generator
```

Parsers: **Docling** (IBM), **MarkItDown** (Microsoft), **Unstructured**, **PyMuPDF**, **pdfplumber**, **python-docx**.

Metrics computed per file × parser:
- Text quality: word count, char count, heading count, table rows, blank-line ratio
- Field detection: email, phone, URL, section coverage (20 resume section keywords)
- Layout: ROUGE-1 recall/precision/F1 vs `.txt` reference when available
- Performance: wall-clock time (s), peak memory (MB)

Results land in `src/benchmarking/results/` (gitignored). The HTML report includes a colour-coded heatmap.

**Adding a new parser**: subclass `BaseParser` in `src/benchmarking/parsers/`, implement `name`, `supports()`, and `_parse()`, then add the class to `_PARSER_CLASSES` in `parsers/__init__.py`.

## Key files

| File | Purpose |
|------|---------|
| `src/main.py` | Entry point; set `MODE` and `FILE_PATH` here |
| `src/llm_based/core/interfaces.py` | All abstract base classes |
| `src/llm_based/core/models.py` | Pydantic models: `ResumeDocument`, `ExtractedResume`, `LLMRequest/Response` |
| `src/llm_based/config/settings.py` | All configuration loaded from env |
| `src/llm_based/config/prompts.yaml` | LLM prompts (edit here, not in code) |
| `src/llm_based/services/parser_service.py` | Top-level orchestration for single and batch parsing |
| `src/llm_based/example_usage.py` | End-to-end wiring example |
| `src/.env.example` | Template for required environment variables |
| `src/benchmarking/benchmark_runner.py` | Run all parsers across all data files |
| `src/benchmarking/report_generator.py` | Produce CSV + HTML benchmark report |
| `src/benchmarking/parsers/base_parser.py` | ABC for adding new parsers |
