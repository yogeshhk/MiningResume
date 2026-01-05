"""
Parser service - main orchestration service for resume parsing.

Coordinates document reading, text extraction, and LLM-based attribute extraction.
"""

import time
from pathlib import Path
from typing import List, Optional
from collections import OrderedDict

from ..core.interfaces import IParserService, IDocumentReader, ITextExtractor
from ..core.models import ParserConfig, ParserResult, ExtractedResume, ResumeDocument
from ..core.exceptions import ParserException
from ..services.llm_service import LLMService
from ..utils.logger import get_logger
from ..utils.metrics import get_metrics_collector, PerformanceTimer
from ..utils.validators import ResumeDataValidator

logger = get_logger(__name__)


class ParserService(IParserService):
    """Main service for orchestrating resume parsing operations."""

    def __init__(
        self,
        document_reader: IDocumentReader,
        text_extractor: ITextExtractor,
        llm_service: LLMService,
        config: Optional[ParserConfig] = None,
    ):
        """
        Initialize parser service.

        Args:
            document_reader: Document reader service
            text_extractor: Text extraction service
            llm_service: LLM service for attribute extraction
            config: Parser configuration
        """
        self.document_reader = document_reader
        self.text_extractor = text_extractor
        self.llm_service = llm_service
        self.config = config or ParserConfig()
        self.validator = ResumeDataValidator()
        self.metrics = get_metrics_collector()

        logger.info(
            "Initialized parser service",
            model=self.config.model_name,
            attributes_count=len(self.config.attributes_to_extract)
        )

    def parse_single(self, file_path: Path, config: Optional[ParserConfig] = None) -> ParserResult:
        """
        Parse a single resume file.

        Args:
            file_path: Path to the resume file
            config: Optional parser configuration override

        Returns:
            ParserResult with extracted data or error information
        """
        # Use provided config or default
        parse_config = config or self.config

        # Ensure Path object
        if not isinstance(file_path, Path):
            file_path = Path(file_path)

        start_time = time.time()
        llm_calls = 0
        cache_hits = 0

        logger.info(f"Starting parse for {file_path.name}")

        try:
            with PerformanceTimer(f"parse_{file_path.name}"):
                # Step 1: Read document
                document = self._read_document(file_path)

                # Step 2: Extract text
                resume_text = self._extract_text(document)

                # Step 3: Extract attributes using LLM
                extracted_data = self._extract_attributes(
                    resume_text,
                    document.filename,
                    parse_config.attributes_to_extract
                )

                # Step 4: Validate extracted data
                self.validator.validate_extracted_data(extracted_data)

                # Calculate metrics
                processing_time = time.time() - start_time

                # Get LLM metrics
                current_metrics = self.metrics.get_summary()
                llm_calls = current_metrics["counters"].get("llm_calls", 0)
                cache_hits = current_metrics["counters"].get("cache_hits", 0)

                logger.info(
                    f"Successfully parsed {file_path.name}",
                    processing_time=f"{processing_time:.2f}s",
                    llm_calls=llm_calls,
                    cache_hits=cache_hits
                )

                return ParserResult(
                    success=True,
                    extracted_data=extracted_data,
                    processing_time_seconds=processing_time,
                    llm_calls_count=llm_calls,
                    cache_hits_count=cache_hits,
                )

        except Exception as e:
            processing_time = time.time() - start_time

            logger.error(
                f"Failed to parse {file_path.name}: {e}",
                processing_time=f"{processing_time:.2f}s",
                error_type=type(e).__name__
            )

            return ParserResult(
                success=False,
                error_message=str(e),
                error_details={
                    "error_type": type(e).__name__,
                    "file_path": str(file_path),
                },
                processing_time_seconds=processing_time,
            )

    def parse_batch(
        self, file_paths: List[Path], config: Optional[ParserConfig] = None
    ) -> List[ParserResult]:
        """
        Parse multiple resume files.

        Args:
            file_paths: List of paths to resume files
            config: Optional parser configuration override

        Returns:
            List of ParserResult for each file
        """
        parse_config = config or self.config
        results = []

        logger.info(f"Starting batch parse for {len(file_paths)} files")

        for i, file_path in enumerate(file_paths, 1):
            logger.info(f"Processing file {i}/{len(file_paths)}: {file_path.name}")

            try:
                result = self.parse_single(file_path, parse_config)
                results.append(result)

                # Stop on first error if fail_fast is enabled
                if not result.success and parse_config.fail_fast:
                    logger.warning(
                        "Stopping batch processing due to error (fail_fast=True)",
                        failed_file=file_path.name
                    )
                    break

            except Exception as e:
                logger.error(f"Unexpected error processing {file_path.name}: {e}")

                if parse_config.fail_fast:
                    raise

                # Add error result
                results.append(
                    ParserResult(
                        success=False,
                        error_message=str(e),
                        processing_time_seconds=0.0,
                    )
                )

        successful = sum(1 for r in results if r.success)
        logger.info(
            f"Batch processing complete: {successful}/{len(results)} successful",
            total_files=len(file_paths),
            processed=len(results)
        )

        return results

    def _read_document(self, file_path: Path) -> ResumeDocument:
        """
        Read document with error handling.

        Args:
            file_path: Path to document

        Returns:
            ResumeDocument
        """
        try:
            return self.document_reader.read_document(file_path)
        except Exception as e:
            logger.error(f"Document read failed: {e}", file=str(file_path))
            raise

    def _extract_text(self, document: ResumeDocument) -> str:
        """
        Extract text with error handling.

        Args:
            document: Resume document

        Returns:
            Extracted text
        """
        try:
            return self.text_extractor.extract_text(document)
        except Exception as e:
            logger.error(f"Text extraction failed: {e}", file=document.filename)
            raise

    def _extract_attributes(
        self, resume_text: str, filename: str, attributes: List[str]
    ) -> ExtractedResume:
        """
        Extract attributes from resume text using LLM.

        Args:
            resume_text: The resume text
            filename: Source filename
            attributes: List of attributes to extract

        Returns:
            ExtractedResume with extracted data
        """
        extracted_dict = OrderedDict()
        extracted_dict["filename"] = filename

        for attr in attributes:
            try:
                logger.debug(f"Extracting attribute: {attr}", file=filename)
                value = self.llm_service.extract_attribute(resume_text, attr)

                # Map attribute to field name (handle spaces and special chars)
                field_name = attr.lower().replace(" ", "_").replace("-", "_")
                extracted_dict[field_name] = value

            except Exception as e:
                logger.warning(
                    f"Failed to extract {attr}: {e}",
                    file=filename
                )
                # Set empty value on failure (partial results)
                field_name = attr.lower().replace(" ", "_").replace("-", "_")
                extracted_dict[field_name] = ""

        # Create ExtractedResume model
        try:
            return ExtractedResume(**extracted_dict)
        except Exception as e:
            logger.error(f"Failed to create ExtractedResume model: {e}")
            # Create with minimal data
            return ExtractedResume(filename=filename)

