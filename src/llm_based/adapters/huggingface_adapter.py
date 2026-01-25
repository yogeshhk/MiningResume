"""
HuggingFace adapter for LLM operations.

Implements the ILLMProvider interface for HuggingFace models.
"""

import os
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

    def __init__(self):
        """
        Initialize HuggingFace adapter.
        """
        self.llm = None
        try:
            if settings.use_local_llm:
                self.llm = self._initialize_local_model()
            else:
                self.llm = self._initialize_api_model()

            logger.info(f"HuggingFace adapter initialized successfully")

        except Exception as e:
            logger.error(f"Failed to initialize HuggingFace adapter: {e}")
            raise LLMServiceError(
                f"Failed to initialize HuggingFace model: {e}",
                details={"model": settings.llm_model_name, "use_local": settings.use_local_llm}
            ) from e

    def _initialize_local_model(self):
        """Initialize local HuggingFace model."""
        logger.info(f"Loading local model: {settings.llm_model_name}")

        try:
            # Enforce strictly-local behavior: prevent any network calls
            os.environ.setdefault("TRANSFORMERS_OFFLINE", "1")
            os.environ.setdefault("HF_HUB_OFFLINE", "1")

            # Create pipeline for text2text generation using only local files
            pipe = pipeline(
                "text2text-generation",
                model=settings.llm_model_name,
                tokenizer=settings.llm_model_name,
                max_new_tokens=settings.llm_max_tokens,
                token=False,  # Don't require token for local models
            )

            # Attempt to capture and log local paths of loaded artifacts
            model_path = getattr(getattr(pipe, "model", None), "name_or_path", None)
            tokenizer_path = getattr(getattr(pipe, "tokenizer", None), "name_or_path", None)
            paths = []
            if isinstance(model_path, str) and os.path.exists(model_path):
                paths.append(os.path.abspath(model_path))
            if isinstance(tokenizer_path, str) and os.path.exists(tokenizer_path):
                paths.append(os.path.abspath(tokenizer_path))
            if paths:
                logger.info(
                    "Using local HuggingFace artifacts",
                    model_paths=paths,
                )

            # Wrap in LangChain
            return HuggingFacePipeline(pipeline=pipe)

        except Exception as e:
            # Provide a clear message if local files are missing and prevent silent hub downloads
            logger.error(
                "Failed to load local model strictly offline",
                error=str(e),
                model=settings.llm_model_name,
                hint=(
                    "Model/tokenizer must be available locally. "
                    "If using a Hub ID, pre-download the files to cache or specify a local directory path. "
                    "You can prefetch via a connected environment and then run offline, or set model_name to a folder containing "
                    "config.json, tokenizer files, and model weights."
                ),
            )
            raise

    def _initialize_api_model(self):
        """Initialize HuggingFace API-based model."""
        from langchain_huggingface import HuggingFaceEndpoint

        logger.info(f"Connecting to HuggingFace API: {settings.llm_model_name}")

        # Ensure offline env flags do not interfere with API usage
        for var in ("TRANSFORMERS_OFFLINE", "HF_HUB_OFFLINE"):
            if os.environ.get(var):
                logger.debug("Unsetting offline environment flag", flag=var)
                os.environ.pop(var, None)

        if not settings.hf_api_token:
            raise LLMServiceError(
                "HuggingFace API token required but not found",
                details={
                    "env_vars_checked": ["HUGGING_FACE_HUB_API_TOKEN", "HF_API_TOKEN"]
                }
            )

        try:
            return HuggingFaceEndpoint(
                repo_id=settings.llm_model_name,
                temperature=settings.llm_temperature,
                huggingfacehub_api_token=settings.hf_api_token,
                max_new_tokens=settings.llm_max_tokens,
                timeout=settings.llm_timeout_seconds,
            )
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
                )

            except TimeoutError as e:
                raise LLMTimeoutError(
                    f"LLM request timed out: {e}",
                    details={"attribute": request.attribute, "model": settings.llm_model_name}
                ) from e

        except LLMTimeoutError:
            raise
        except Exception as e:
            logger.error(f"LLM generation failed: {e}", attribute=request.attribute)
            raise LLMServiceError(
                f"Failed to generate response: {e}",
                details={
                    "attribute": request.attribute,
                    "model": settings.llm_model_name,
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
            # Try a simple generation
            test_request = LLMRequest(
                prompt="Say 'OK'",
                context="",
                attribute="health_check"
            )

            self.generate(test_request)

            logger.info("Health check passed")
            return True

        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return False

