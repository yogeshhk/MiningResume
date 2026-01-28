"""
LLM service for interacting with Large Language Models.

Provides an abstraction layer over different LLM providers.
"""

import time
import yaml
from typing import Optional, Dict, Any

from src.llm_based.core.interfaces import ILLMProvider, ICacheService
from src.llm_based.core.models import LLMRequest, LLMResponse
from src.llm_based.core.exceptions import LLMServiceError, LLMTimeoutError
from src.llm_based.utils.logger import get_logger
from src.llm_based.utils.retry import retry_with_backoff
from src.llm_based.utils.metrics import TokenCounter, get_metrics_collector
from src.llm_based.services.cache_service import CacheKeyGenerator
from src.llm_based.config.settings import settings

logger = get_logger(__name__)


class LLMService:
    """Service for managing LLM interactions with caching and retry logic."""

    def __init__(
        self,
        provider: ILLMProvider,
        cache_service: Optional[ICacheService] = None,
    ):
        """
        Initialize LLM service.

        Args:
            provider: LLM provider implementation
            cache_service: Optional cache service for responses
        """
        self.provider = provider
        self.cache_service = cache_service
        self.metrics = get_metrics_collector()
        self.prompts = self._load_prompts()

        logger.info(
            f"Initialized LLM service with '{settings.llm_provider}' provider",
            model=settings.llm_model_name,
            cache_enabled=cache_service is not None
        )

    def _load_prompts(self) -> Dict[str, Any]:
        """
        Load prompt templates from configuration.

        Returns:
            Dictionary of prompt templates
        """
        try:
            prompts_file = settings.prompts_file

            if prompts_file.exists():
                with open(prompts_file, 'r') as f:
                    prompts = yaml.safe_load(f)
                logger.debug("Loaded prompt templates", file=str(prompts_file))
                return prompts
            else:
                logger.warning(f"Prompts file not found: {prompts_file}, using defaults")
                return self._get_default_prompts()

        except Exception as e:
            logger.error(f"Failed to load prompts: {e}")
            return self._get_default_prompts()

    def _get_default_prompts(self) -> Dict[str, Any]:
        """Get default prompt templates."""
        return {
            "system_prompt": "You are an expert recruiter skilled at extracting relevant information from resumes.",
            "extraction": {
                "user_prompt_template": "Extract {attribute} from the following resume text.\n\nResume:\n{resume}\n\nExtracted {attribute}:",
            }
        }

    def generate(self, request: LLMRequest) -> LLMResponse:
        """
        Generate a response from the LLM with caching and retry.

        Args:
            request: LLM request

        Returns:
            LLM response

        Raises:
            LLMServiceError: If generation fails
        """
        # Check cache first
        cache_key = None
        if self.cache_service and settings.cache_enabled:
            cache_key = CacheKeyGenerator.generate_key(
                request.prompt, request.context, request.attribute
            )
            cached_response = self.cache_service.get(cache_key)

            if cached_response:
                logger.debug(f"Cache hit for attribute: {request.attribute}")
                self.metrics.increment_counter("cache_hits")

                return LLMResponse(
                    content=cached_response,
                    attribute=request.attribute
                )

        # Generate with retry
        try:
            response = self._generate_with_retry(request)

            # Cache the response
            if self.cache_service and settings.cache_enabled:
                self.cache_service.set(cache_key, response.content, settings.cache_ttl_seconds)

            self.metrics.increment_counter("llm_calls")
            return response

        except Exception as e:
            logger.error(f"LLM generation failed: {e}", attribute=request.attribute)
            raise LLMServiceError(
                f"Failed to generate response: {e}",
                details={"attribute": request.attribute, "error": str(e)}
            ) from e

    @retry_with_backoff(
        max_attempts=3,
        initial_wait=1.0,
        backoff_factor=2.0,
        exceptions=(LLMServiceError, LLMTimeoutError),
    )
    def _generate_with_retry(self, request: LLMRequest) -> LLMResponse:
        """
        Generate response with retry logic.

        Args:
            request: LLM request

        Returns:
            LLM response
        """
        start_time = time.time()

        try:
            response = self.provider.generate(request)

            # Track metrics
            latency_ms = (time.time() - start_time) * 1000
            response.latency_ms = latency_ms

            # Track token usage
            if not response.tokens_used:
                token_usage = TokenCounter.track_token_usage(
                    request.prompt + request.context,
                    response.content,
                    model=settings.llm_model_name
                )
                response.tokens_used = token_usage["total_tokens"]

            logger.debug(
                f"LLM response generated for {request.attribute}",
                latency_ms=latency_ms,
                tokens_used=response.tokens_used
            )

            return response

        except Exception as e:
            logger.error(f"LLM provider error: {e}", attribute=request.attribute)
            raise

    def extract_attribute(self, resume_text: str, attribute: str) -> str:
        """
        Extract a specific attribute from resume text.

        Args:
            resume_text: The resume text
            attribute: The attribute to extract

        Returns:
            Extracted value as string
        """
        # Build prompt
        prompt = self._build_prompt(attribute)

        # Create request
        request = LLMRequest(
            prompt=prompt,
            context=resume_text,
            attribute=attribute
        )

        # Generate response
        response = self.generate(request)

        return response.content.strip()

    def _build_prompt(self, attribute: str) -> str:
        """
        Build a prompt for extracting an attribute.

        Args:
            attribute: The attribute to extract

        Returns:
            Formatted prompt string
        """
        # Check for attribute-specific prompt
        if "extraction" in self.prompts:
            extraction_prompts = self.prompts["extraction"]

            # Check for specific attribute prompt
            if "extracted_attributes" in extraction_prompts and attribute in extraction_prompts["extracted_attributes"]:
                template = extraction_prompts["extracted_attributes"][attribute].get("prompt")
                if template:
                    return template

            # Use default template
            if "user_prompt_template" in extraction_prompts:
                return extraction_prompts["user_prompt_template"]

        # Fallback to simple prompt
        return f"Extract {attribute} from the following resume text.\n\nResume:\n{{resume}}\n\nExtracted {attribute}:"

    def health_check(self) -> bool:
        """
        Check if the LLM service is healthy.

        Returns:
            True if service is healthy
        """
        try:
            return self.provider.health_check()
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return False

    #This will be used for chatbot functionality
    def ask(self, prompt: str, max_tokens: int = 512) -> str:
        """
        Ask a free-form question to the LLM.
        """
        request = LLMRequest(
            prompt="{resume}",
            context=prompt,
            attribute="chat"
        )

        response = self.generate(request)
        return response.content
