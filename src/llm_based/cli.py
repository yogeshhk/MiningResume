"""
Command-line interface for the LLM Resume Parser.

Provides a user-friendly CLI for parsing resumes.
"""

import sys
import json
import argparse
from pathlib import Path
from typing import List

from src.llm_based.core.models import ParserConfig, FileFormat
from src.llm_based.core.exceptions import ParserException
from src.llm_based.services.document_reader import BaseDocumentReader
from src.llm_based.services.text_extractor import TextExtractorService
from src.llm_based.services.llm_service import LLMService
from src.llm_based.services.parser_service import ParserService
from src.llm_based.services.cache_service import create_cache_service
from src.llm_based.adapters.file_adapters import create_text_extractor_for_format
from src.llm_based.adapters.huggingface_adapter import HuggingFaceAdapter
from src.llm_based.config.settings import settings
from src.llm_based.utils.logger import get_logger
from src.llm_based.utils.metrics import get_metrics_collector

logger = get_logger(__name__)


def setup_parser_service(config: ParserConfig) -> ParserService:
    """
    Set up the parser service with all dependencies.

    Args:
        config: Parser configuration

    Returns:
        Configured ParserService instance
    """
    logger.info("Setting up parser service")

    # Create document reader
    document_reader = BaseDocumentReader()

    # Create text extractor service
    text_extractor = TextExtractorService()

    # Register format-specific extractors
    for file_format in FileFormat:
        try:
            extractor = create_text_extractor_for_format(file_format)
            text_extractor.register_extractor(file_format, extractor)
            logger.debug(f"Registered extractor for {file_format.value}")
        except Exception as e:
            logger.warning(f"Failed to register extractor for {file_format.value}: {e}")

    # Create cache service
    cache_service = None
    if config.cache_enabled:
        cache_service = create_cache_service(
            backend=settings.cache_backend,
            default_ttl_seconds=config.cache_ttl_seconds
        )

    # Create LLM provider (HuggingFace)
    llm_provider = HuggingFaceAdapter(
        model_name=config.model_name,
        use_local=settings.huggingface_use_local,
    )

    # Create LLM service
    llm_service = LLMService(
        provider=llm_provider,
        config=config,
        cache_service=cache_service,
    )

    # Create parser service
    parser_service = ParserService(
        document_reader=document_reader,
        text_extractor=text_extractor,
        llm_service=llm_service,
        config=config,
    )

    logger.info("Parser service setup complete")
    return parser_service


def parse_single_file(file_path: Path, config: ParserConfig, output_format: str = "json") -> None:
    """
    Parse a single resume file.

    Args:
        file_path: Path to the resume file
        config: Parser configuration
        output_format: Output format (json or yaml)
    """
    logger.info(f"Parsing single file: {file_path}")

    # Setup parser service
    parser_service = setup_parser_service(config)

    # Parse the file
    result = parser_service.parse_single(file_path, config)

    # Output results
    if result.success:
        print(f"\n✅ Successfully parsed: {file_path.name}")
        print(f"\n--- Extracted Data ---")

        if output_format == "json":
            print(result.extracted_data.to_json(indent=2))
        else:
            # Simple text output
            data_dict = result.extracted_data.to_dict()
            for key, value in data_dict.items():
                if value:
                    print(f"{key}: {value}")

        # Print metrics
        metrics = get_metrics_collector().get_summary()
        print(f"\n--- Metrics ---")
        print(f"Processing time: {result.processing_time_seconds:.2f}s")
        print(f"LLM calls: {result.llm_calls_count}")
        print(f"Cache hits: {result.cache_hits_count}")

    else:
        print(f"\n❌ Failed to parse: {file_path.name}")
        print(f"Error: {result.error_message}")
        if result.error_details:
            print(f"Details: {json.dumps(result.error_details, indent=2)}")
        sys.exit(1)


def parse_folder(folder_path: Path, config: ParserConfig, output_format: str = "json") -> None:
    """
    Parse all resume files in a folder.

    Args:
        folder_path: Path to the folder
        config: Parser configuration
        output_format: Output format (json or yaml)
    """
    logger.info(f"Parsing folder: {folder_path}")

    # Find all supported files
    file_paths: List[Path] = []
    for ext in ["pdf", "docx", "txt"]:
        file_paths.extend(folder_path.glob(f"*.{ext}"))
        file_paths.extend(folder_path.glob(f"*.{ext.upper()}"))

    if not file_paths:
        print(f"❌ No resume files found in: {folder_path}")
        sys.exit(1)

    print(f"\nFound {len(file_paths)} resume file(s)")

    # Setup parser service
    parser_service = setup_parser_service(config)

    # Parse all files
    results = parser_service.parse_batch(file_paths, config)

    # Output results
    successful = sum(1 for r in results if r.success)
    print(f"\n--- Batch Processing Complete ---")
    print(f"Total: {len(results)} files")
    print(f"Successful: {successful}")
    print(f"Failed: {len(results) - successful}")

    # Output each result
    all_results = []
    for result in results:
        if result.success:
            all_results.append(result.extracted_data.to_dict())
        else:
            print(f"\n❌ Failed: {result.error_message}")

    if all_results:
        print(f"\n--- All Extracted Data ---")
        print(json.dumps(all_results, indent=2))

    # Print summary metrics
    metrics = get_metrics_collector().get_summary()
    print(f"\n--- Overall Metrics ---")
    print(f"Average processing time: {metrics['average_duration_seconds']:.2f}s")
    print(f"Total LLM calls: {metrics['counters'].get('llm_calls', 0)}")
    print(f"Total cache hits: {metrics['counters'].get('cache_hits', 0)}")


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="LLM Resume Parser - Extract structured data from resumes using AI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument(
        "command",
        choices=["parse"],
        help="Command to execute"
    )

    parser.add_argument(
        "--file",
        type=Path,
        help="Path to a single resume file to parse"
    )

    parser.add_argument(
        "--folder",
        type=Path,
        help="Path to a folder containing resume files"
    )

    parser.add_argument(
        "--model",
        type=str,
        default=None,
        help=f"LLM model name (default: {settings.llm_model_name})"
    )

    parser.add_argument(
        "--output-format",
        choices=["json", "text"],
        default="json",
        help="Output format (default: json)"
    )

    parser.add_argument(
        "--no-cache",
        action="store_true",
        help="Disable caching"
    )

    parser.add_argument(
        "--fail-fast",
        action="store_true",
        help="Stop on first error when processing multiple files"
    )

    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose logging"
    )

    args = parser.parse_args()

    # Update log level if verbose
    if args.verbose:
        settings.log_level = "DEBUG"
        logger.info("Verbose logging enabled")

    # Validate arguments
    if not args.file and not args.folder:
        print("❌ Error: Must specify either --file or --folder")
        parser.print_help()
        sys.exit(1)

    # Create parser configuration
    config = ParserConfig(
        model_name=args.model or settings.llm_model_name,
        cache_enabled=not args.no_cache,
        fail_fast=args.fail_fast,
    )

    try:
        if args.file:
            if not args.file.exists():
                print(f"❌ Error: File not found: {args.file}")
                sys.exit(1)
            parse_single_file(args.file, config, args.output_format)

        elif args.folder:
            if not args.folder.exists() or not args.folder.is_dir():
                print(f"❌ Error: Folder not found: {args.folder}")
                sys.exit(1)
            parse_folder(args.folder, config, args.output_format)

    except ParserException as e:
        print(f"\n❌ Parser Error: {e}")
        if e.details:
            print(f"Details: {json.dumps(e.details, indent=2)}")
        sys.exit(1)

    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user")
        sys.exit(130)

    except Exception as e:
        logger.exception("Unexpected error occurred")
        print(f"\n❌ Unexpected Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

