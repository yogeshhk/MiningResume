"""
Ollama adapter for LLM operations.

Implements the ILLMProvider interface for Ollama models.
"""
from langchain_core.messages import AIMessage
from langchain_ollama import ChatOllama

from src.llm_based.core.interfaces import ILLMProvider
from src.llm_based.core.models import LLMRequest, LLMResponse
from src.llm_based.core.exceptions import LLMServiceError, LLMTimeoutError
from src.llm_based.config.settings import settings
from src.llm_based.utils.logger import get_logger

logger = get_logger(__name__)


class OllamaAdapter(ILLMProvider):
    """Ollama implementation of ILLMProvider."""

    def __init__(self):
        """
        Initialize Ollama adapter.
        """
        self.llm = None
        try:
            if settings.use_local_llm:
                self.llm = self._initialize_local_model()
            else:
                self.llm = self._initialize_api_model()

            logger.info(f"Ollama adapter initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Ollama adapter: {e}")
            raise LLMServiceError(
                f"Failed to initialize Ollama model: {e}",
                details={"model": settings.llm_model_name, "use_local": settings.use_local_llm}
            ) from e

    def _initialize_local_model(self):
        """Initialize local Ollama model."""
        return ChatOllama(
            model=settings.llm_model_name,
            base_url=settings.ollama_api_url
        )

    def _initialize_api_model(self):
        raise NotImplementedError("Ollama cloud integration endpoint initialization not implemented yet.")

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
                if isinstance(response_text, AIMessage):
                    content = response_text.text
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
