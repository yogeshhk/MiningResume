"""
HuggingFace adapter for LLM operations.

Implements the ILLMProvider interface for HuggingFace models.
"""

import os
from typing import Optional
from transformers import pipeline
from langchain_community.llms import HuggingFacePipeline

from src.llm_based.core.interfaces import ILLMProvider
from src.llm_based.core.models import LLMRequest, LLMResponse
from src.llm_based.core.exceptions import LLMServiceError, LLMTimeoutError
from src.llm_based.config.settings import settings
from src.llm_based.utils.logger import get_logger

logger = get_logger(__name__)


class HuggingFaceAdapter(ILLMProvider):
    """HuggingFace implementation of ILLMProvider."""

    def __init__(
        self,
        model_name: Optional[str] = None,
        use_local: bool = True,
        api_token: Optional[str] = None,
    ):
        """
        Initialize HuggingFace adapter.

        Args:
            model_name: Model name/identifier
            use_local: Whether to use local model instead of API
            api_token: HuggingFace API token (for API usage)
        """
        self.model_name = model_name or settings.llm_model_name
        self.use_local = use_local
        self.api_token = api_token or settings.get_hf_token()
        self.llm = None
        self._initialized = False

        logger.info(
            "Initializing HuggingFace adapter",
            model=self.model_name,
            use_local=self.use_local
        )

    def _initialize(self) -> None:
        """Lazy initialization of the model."""
        if self._initialized:
            return

        try:
            if self.use_local:
                self._initialize_local_model()
            else:
                self._initialize_api_model()

            self._initialized = True
            logger.info(f"HuggingFace adapter initialized successfully")

        except Exception as e:
            logger.error(f"Failed to initialize HuggingFace adapter: {e}")
            raise LLMServiceError(
                f"Failed to initialize HuggingFace model: {e}",
                details={"model": self.model_name, "use_local": self.use_local}
            ) from e

    def _initialize_local_model(self) -> None:
        """Initialize local HuggingFace model."""
        logger.info(f"Loading local model: {self.model_name}")

        try:
            # Create pipeline for text2text generation
            pipe = pipeline(
                "text2text-generation",
                model=self.model_name,
                tokenizer=self.model_name,
                max_new_tokens=settings.llm_max_tokens,
                token=False,  # Don't require token for local models
            )

            # Wrap in LangChain
            self.llm = HuggingFacePipeline(pipeline=pipe)

            logger.info(f"Local model loaded successfully: {self.model_name}")

        except Exception as e:
            logger.error(f"Failed to load local model: {e}")
            raise

    def _initialize_api_model(self) -> None:
        """Initialize HuggingFace API-based model."""
        from langchain_huggingface import HuggingFaceEndpoint

        logger.info(f"Connecting to HuggingFace API: {self.model_name}")

        if not self.api_token:
            raise LLMServiceError(
                "HuggingFace API token required but not found",
                details={
                    "env_vars_checked": ["HUGGINGFACEHUB_API_TOKEN", "HF_API_TOKEN"]
                }
            )

        try:
            self.llm = HuggingFaceEndpoint(
                repo_id=self.model_name,
                temperature=settings.llm_temperature,
                huggingfacehub_api_token=self.api_token,
                max_new_tokens=settings.llm_max_tokens,
                timeout=settings.llm_timeout_seconds,
            )

            logger.info(f"Connected to HuggingFace API successfully")

        except Exception as e:
            logger.error(f"Failed to connect to HuggingFace API: {e}")
            raise

    def generate(self, request: LLMRequest) -> LLMResponse:
        """
        Generate a response from the LLM.

        Args:
            request: The LLM request with prompt and context

        Returns:
            LLMResponse with generated content

        Raises:
            LLMServiceError: If LLM call fails
        """
        # Initialize model if needed
        if not self._initialized:
            self._initialize()

        try:
            # Build full prompt
            full_prompt = request.prompt.format(
                resume=request.context,
                attribute=request.attribute
            )

            logger.debug(
                f"Generating response for attribute: {request.attribute}",
                prompt_length=len(full_prompt)
            )

            # Generate response
            try:
                response_text = self.llm.invoke(full_prompt)

                # Handle different response types
                if isinstance(response_text, dict) and "text" in response_text:
                    content = response_text["text"]
                else:
                    content = str(response_text)

                logger.debug(
                    f"Generated response for {request.attribute}",
                    response_length=len(content)
                )

                return LLMResponse(
                    content=content.strip(),
                    attribute=request.attribute,
                    model_name=self.model_name,
                    cached=False,
                )

            except TimeoutError as e:
                raise LLMTimeoutError(
                    f"LLM request timed out: {e}",
                    details={"attribute": request.attribute, "model": self.model_name}
                ) from e

        except LLMTimeoutError:
            raise
        except Exception as e:
            logger.error(f"LLM generation failed: {e}", attribute=request.attribute)
            raise LLMServiceError(
                f"Failed to generate response: {e}",
                details={
                    "attribute": request.attribute,
                    "model": self.model_name,
                    "error_type": type(e).__name__,
                }
            ) from e

    def health_check(self) -> bool:
        """
        Check if the LLM service is healthy and accessible.

        Returns:
            True if service is healthy
        """
        try:
            # Try to initialize if not already done
            if not self._initialized:
                self._initialize()

            # Try a simple generation
            test_request = LLMRequest(
                prompt="Say 'OK'",
                context="",
                attribute="health_check",
                max_tokens=10,
            )

            response = self.generate(test_request)

            logger.info("Health check passed")
            return True

        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return False

    def get_provider_name(self) -> str:
        """
        Get the name of the LLM provider.

        Returns:
            Provider name
        """
        return "huggingface"

    def get_model_info(self) -> dict:
        """
        Get information about the loaded model.

        Returns:
            Dictionary with model information
        """
        return {
            "provider": self.get_provider_name(),
            "model_name": self.model_name,
            "use_local": self.use_local,
            "initialized": self._initialized,
        }
