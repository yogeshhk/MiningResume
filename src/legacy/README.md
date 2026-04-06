# legacy

Contains earlier parser implementations kept for historical reference. None of these files are imported by the current codebase.

| File | Description |
|------|-------------|
| `llm_resume_parser.py` | Original v1.0 LLM parser — monolithic, single-file implementation that preceded the SOLID v2.0 architecture in `src/llm_based/` |
| `docling_resume_parser.py` | Experimental parser using the Docling library for document ingestion |
| `huggingface_api_test.py` | Scratch script for testing HuggingFace API connectivity before the adapter pattern was introduced |

## Migration note

The production code is in `src/llm_based/`. If you need to understand what changed between v1 and v2, compare `llm_resume_parser.py` against `src/llm_based/services/parser_service.py` and the adapter layer.
