"""
Example script demonstrating usage of the LLM Resume Parser.

This shows how to use the parser programmatically.
"""
from pathlib import Path

from src.llm_based.services.document_reader import BaseDocumentReader
from src.llm_based.services.text_extractor import TextExtractorService
from src.llm_based.services.llm_service import LLMService
from src.llm_based.services.parser_service import ParserService
from src.llm_based.services.cache_service import create_cache_service
from src.llm_based.adapters.file_adapters import create_text_extractor_for_format
from src.llm_based.adapters.huggingface_adapter import HuggingFaceAdapter
from src.llm_based.adapters.ollama_adapter import OllamaAdapter
from src.llm_based.core.models import FileFormat
from src.llm_based.config.settings import settings


def setup_parser():
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


def main():
    """Main example execution."""

    print("=== LLM Resume Parser Example ===\n")

    # Get sample resume path
    data_folder = Path(__file__).parent.parent.parent / "data"
    sample_resume = data_folder / "YogeshKulkarniLinkedInProfile.pdf"

    if not sample_resume.exists():
        print(f"Error: Sample resume not found at {sample_resume}")
        print("Please place a resume file in the data folder.")
        return

    print(f"Setting up parser...")
    parser = setup_parser()

    print(f"Parsing: {sample_resume.name}\n")

    # Parse the resume
    result = parser.parse_single(sample_resume)

    # Display results
    if result.success:
        print("✅ Parsing successful!\n")
        print("--- Extracted Data ---")
        print(result.extracted_data.to_json(indent=2))

        print(f"\n--- Metrics ---")
        print(f"Processing time: {result.processing_time_seconds:.2f}s")
        print(f"LLM calls: {result.llm_calls_count}")
        print(f"Cache hits: {result.cache_hits_count}")
    else:
        print("❌ Parsing failed!")
        print(f"Error: {result.error_message}")


if __name__ == "__main__":
    main()

