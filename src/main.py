# Minimal entry point with a simple mode switch (Option C)
# Set MODE to "rule" for rule-based regex parser, or "llm" for LLM-based pipeline.
# Adjust FILE_PATH to point to a resume under the repository's data folder.

import json
from pathlib import Path

from src.llm_based.adapters import create_text_extractor_for_format, HuggingFaceAdapter
from src.llm_based.adapters.ollama_adapter import OllamaAdapter
from src.llm_based.config import settings
from src.llm_based.core import FileFormat
from src.llm_based.services import BaseDocumentReader, TextExtractorService, create_cache_service, LLMService, ParserService, Neo4jService
from src.llm_based.config.settings import settings

# ---- Configuration (edit these constants as needed) ----
MODE = "llm"  # "rule" or "llm"
FILE_PATH = Path(__file__).resolve().parent.parent / "data" / "test6.pdf"
# -------------------------------------------------------


def run_rule_based(file_path: Path) -> None:
    """Run the rule-based parser using regex configuration."""
    from src.rule_based.regex_resume_parser import RegexResumeParser

    # Load regex configuration XML from the rule_based folder
    config_file = Path(__file__).resolve().parent / "rule_based" / "regex_config.xml"
    if not config_file.exists():
        raise FileNotFoundError(f"Regex config not found: {config_file}")

    with open(config_file, "r", encoding="utf-8") as f:
        config_content = f.read()

    parser = RegexResumeParser(config_content=config_content)
    resume_data = parser.read_resume_file(str(file_path))
    if not resume_data or not resume_data.get("resume_text", "").strip():
        raise RuntimeError(f"Failed to read resume text from: {file_path}")

    result = parser.parse() or {}
    result["filename"] = file_path.name

    print(json.dumps(result, indent=2))


def run_llm_based(file_path: Path) -> None:
    """Run the LLM-based pipeline with minimal wiring."""
    print("=== LLM Resume Parser Example ===\n")

    if not FILE_PATH.exists():
        print(f"Error: Sample resume not found at {FILE_PATH}")
        print("Please place a resume file in the data folder.")
        return

    #TODO: Refactor to a common setup function shared with example_usage.py
    def setup_parser():
        print("Setting up document reader, text extractor, cache, LLM service, and parser...")
        # Create document reader
        document_reader = BaseDocumentReader()

        # Create text extractor service
        text_extractor = TextExtractorService()

        # Register format-specific extractors
        for file_format in FileFormat:
            extractor = create_text_extractor_for_format(file_format)
            text_extractor.register_extractor(file_format, extractor)

        # Create cache service
        cache_service = create_cache_service()

        # Create LLM provider
        if settings.llm_provider.lower() == "huggingface":
            llm_provider = HuggingFaceAdapter()
        elif settings.llm_provider.lower() == "ollama":
            llm_provider = OllamaAdapter()
        else:
            raise ValueError(f"Unsupported LLM provider: {settings.llm_provider}")

        # Create LLM service
        llm_service = LLMService(
            provider=llm_provider,
            cache_service=cache_service,
        )

        # Create parser service
        parser_service = ParserService(
            document_reader=document_reader,
            text_extractor=text_extractor,
            llm_service=llm_service,
        )

        return parser_service

    print(f"Setting up parser...")
    parser = setup_parser()

    print(f"Parsing: {FILE_PATH.name}\n")

    # Parse the resume
    result = parser.parse_single(FILE_PATH)

    # Display results
    if result.success:
        print("✅ Parsing successful!\n")
        print("--- Extracted Data ---")
        print(json.loads(result.extracted_data.model_dump_json()))
        with open("parsed_resume_llm_based.json", "w", encoding="utf-8") as f:
            json.dump(json.loads(result.extracted_data.model_dump_json()), f, indent=2,ensure_ascii=False)
        print(f"\n--- Metrics ---")
        print(f"Processing time: {result.processing_time_seconds:.2f}s")
        print(f"LLM calls: {result.llm_calls_count}")
        print(f"Cache hits: {result.cache_hits_count}")
    else:
        print("❌ Parsing failed!")
        print(f"Error: {result.error_message}")


def main():
    # Minimal switch with clear comments; no external dependencies beyond src.* modules
    file_path = FILE_PATH
    if not file_path.exists():
        raise FileNotFoundError(f"Resume file not found: {file_path}")

    if MODE == "rule":
        run_rule_based(file_path)
    elif MODE == "llm":
        run_llm_based(file_path)
    else:
        raise ValueError(f"Invalid MODE '{MODE}'. Use 'rule' or 'llm'.")

    with open("parsed_resume_llm_based.json", "r", encoding="utf-8") as f:
        resume_data = json.load(f)

    neo4j_service = Neo4jService()

    # overwrite existing resume graph
    neo4j_service.upsert_resume_graph(
        resume_json=resume_data,
        overwrite=True
    )

if __name__ == "__main__":
    main()
