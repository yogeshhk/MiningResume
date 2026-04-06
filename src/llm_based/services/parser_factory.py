"""
Factory function for assembling the ParserService with all dependencies wired.

Import this in entry points (main.py, example_usage.py) instead of repeating
the setup logic.
"""

from src.llm_based.adapters.file_adapters import create_text_extractor_for_format
from src.llm_based.adapters.huggingface_adapter import HuggingFaceAdapter
from src.llm_based.adapters.ollama_adapter import OllamaAdapter
from src.llm_based.config.settings import settings
from src.llm_based.core.models import FileFormat
from src.llm_based.services.cache_service import create_cache_service
from src.llm_based.services.document_reader import BaseDocumentReader
from src.llm_based.services.llm_service import LLMService
from src.llm_based.services.parser_service import ParserService
from src.llm_based.services.text_extractor import TextExtractorService


def create_parser() -> ParserService:
    """
    Assemble and return a fully wired ParserService.

    Reads LLM_PROVIDER from settings to select the appropriate adapter.
    Registers text extractors for all supported file formats.

    Returns:
        ParserService ready to call parse_single() or parse_batch()

    Raises:
        ValueError: If LLM_PROVIDER is not recognised
    """
    document_reader = BaseDocumentReader()

    text_extractor = TextExtractorService()
    for file_format in FileFormat:
        text_extractor.register_extractor(file_format, create_text_extractor_for_format(file_format))

    cache_service = create_cache_service()

    provider_name = settings.llm_provider.lower()
    if provider_name == "huggingface":
        llm_provider = HuggingFaceAdapter()
    elif provider_name == "ollama":
        llm_provider = OllamaAdapter()
    else:
        raise ValueError(
            f"Unsupported LLM provider: '{settings.llm_provider}'. "
            "Set LLM_PROVIDER to 'huggingface' or 'ollama' in your .env file."
        )

    llm_service = LLMService(provider=llm_provider, cache_service=cache_service)

    return ParserService(
        document_reader=document_reader,
        text_extractor=text_extractor,
        llm_service=llm_service,
    )
