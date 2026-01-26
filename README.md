# Mining Resume

This project provides a powerful toolkit for extracting structured information from resume files. It supports various file formats and offers two distinct parsing methodologies: a highly customizable rule-based approach using Regex, and a modern, AI-driven approach using a Large Language Model (LLM).

The primary objective is to convert unstructured resume text from formats like .pdf, .docx, and .txt into a clean, structured JSON output.

## **✨ Features**

* **Multi-Format Support**: Parses resumes from `.pdf`, `.docx`, and `.txt` files seamlessly.  
* **Dual Parsing Engines**:  
  * **Regex-Based Parser**: Offers granular control over data extraction through a simple and powerful XML configuration. Ideal for resumes with consistent formatting.  
  * **LLM-Based Parser**: Leverages Large Language Model configurable as per your choice (locally / hosted) to intelligently identify and extract information, adapting well to varied resume layouts.  
* **Structured Output**: Consistently outputs extracted data in a clean, easy-to-use JSON format.  
* **Customizable Extraction**:  
  * Regex rules are configured in `src/rule_based/regex_config.xml`—no Python changes needed.  
  * LLM extraction attributes and other configuration options available via `src/.env` file.

## **📂 Project Structure**

The repository uses a modular src-based layout:

```
.
├── data/
│   ├── YogeshKulkarniLinkedInProfile.pdf   # Sample resume (add your files here)
│   └── ...
├── src/
│   ├── llm_based/                          # LLM-based parsing architecture
│   │   ├── core/                           # Interfaces, models, exceptions
│   │   ├── services/                       # LLMService, ParserService, etc.
│   │   ├── adapters/                       # LLM providers and file extractors
│   │   ├── utils/                          # Logging, validators, retry, metrics
│   │   ├── config/                         # Settings and prompts.yaml
│   │   ├── example_usage.py                # Example wiring
│   │   └── README.md                       # Package-level docs
│   ├── rule_based/                         # Rule-based (regex) parser
│   │   ├── regex_resume_parser.py
│   │   └── regex_config.xml
│   └── main.py                             # Minimal mode switch (rule vs llm)
├── README.md                               # Root documentation
├── LICENSE
└── ...
```

## **🚀 Getting Started**

Follow these instructions to set up and run the project on your local machine.

### Prerequisites

- Python 3.8+
- For LLM mode (optional): a Hugging Face API token if using the hosted API; for strictly local, ensure the model is cached locally or referenced by a local path.

### Installation

You can install dependencies with either uv (recommended) or pip:

```bash
# Using uv (recommended)
uv pip install --system

# Or, using pip with a requirements file (if present)
# pip install -r requirements.txt
```

You can set these in your shell or a `.env` file (loaded by the application where applicable).

## **🏃 How to Run**

Before running, place the resume files to process in the `data/` folder. Sample files are included.

Use the mode switch in `src/main.py`

- Open `src/main.py` and set the constants at the top:
  - `MODE = "rule"` to use the regex-based parser
  - `MODE = "llm"` to use the LLM-based pipeline
  - `FILE_PATH` points to a resume under `data/`

Run:

```bash
python -m src.main
```

## **⚙️ Configuration**

The **Regex-Based Parser** is controlled by the regex\_config.xml file. This file allows you to define:

* **Terms**: The specific fields to extract (e.g., Name, Email, PhoneNumber).  
* **Methods**: The extraction logic to use (e.g., univalue\_extractor for single values).  
* **Patterns**: The specific regex patterns used to find the information.

This design allows for easy adaptation to different resume formats or extraction requirements without modifying the Python source code.

## **🧱 Architecture Overview**

### LLM-Based Pipeline (`src/llm_based`)
- Core: Interfaces (`ILLMProvider`, `IDocumentReader`, `ITextExtractor`, etc.), models (`ResumeDocument`, `ExtractedResume`, `LLMRequest/Response`), and exceptions.
- Services:
  - `DocumentReader`: validates and reads file metadata
  - `TextExtractorService`: delegates to format-specific extractors (PDF/DOCX/TXT)
  - `LLMService`: loads prompts, handles caching and retry, tracks latency/tokens
  - `ParserService`: orchestrates reading, text extraction, LLM attribute extraction, and validation
- Adapters:
  - File adapters: `PDFTextExtractor`, `DOCXTextExtractor`, `TXTTextExtractor`
  - LLM providers: `HuggingFaceAdapter` (local or API)
- Utils: Structured logger, validators (file/text/data), retry with backoff, metrics (timers and token counting)
- Config: `settings.py` (env-driven), optional `prompts.yaml` (with safe fallback to defaults)

### Rule-Based Engine (`src/rule_based`)
- `regex_resume_parser.py`: parses resumes using patterns from `regex_config.xml`
  - Reads resume text (TXT/PDF/DOCX)
  - Segments content into sections (e.g., Skills, Education)
  - Extracts single-value metadata (name/email/phone) and lists (skills/education) via regex
- `regex_config.xml`: configurable extraction rules (terms, methods, patterns)

### Entry Point
- `src/main.py`: minimal mode switch to run rule-based or LLM-based flows and print JSON output

## **🧪 Testing**

Run the test suite with pytest:

```bash
pytest
```

- Tests and fixtures live under `src/llm_based/tests/` (e.g., `tests/conftest.py`, `tests/unit/`).
- Add unit tests for new features and validators; keep tests fast and deterministic.

## **🤝 Contributing**

Contributions are welcome! Please follow these guidelines to keep the project consistent and maintainable:

- Keep pull requests small and focused; include a clear description of changes.
- Use type hints and docstrings for public functions/classes.
- Add unit tests for new features or bug fixes; keep tests fast and deterministic.
- Follow the existing structured logging style (JSON) and avoid printing directly.
- Update documentation (README or package docs) if behavior changes.

Suggested workflow:
1. Fork the repository and create a feature branch (e.g., `feature/xyz`).
2. Implement changes with tests.
3. Run the test suite locally (`pytest`).
4. Open a pull request describing the motivation and changes.

## 📜 Disclaimer

The author provides no guarantee for the program's results. This is a utility script with room for improvement. Do not depend on it entirely for critical applications.

Copyright (C) 2026 Yogesh H Kulkarni
