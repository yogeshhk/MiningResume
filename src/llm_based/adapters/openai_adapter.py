"""
OpenAI adapter for LLM operations.

Implements the ILLMProvider interface for OpenAI models.
"""

from src.llm_based.core.interfaces import ILLMProvider
from src.llm_based.core.models import LLMRequest, LLMResponse
from src.llm_based.core.exceptions import LLMServiceError
from src.llm_based.utils.logger import get_logger

logger = get_logger(__name__)


class OpenAIAdapter(ILLMProvider):
    """
    OpenAI implementation of ILLMProvider.

    This is a placeholder for future implementation.
    """

    def __init__(self):
        """
        Initialize OpenAI adapter.
        """
        logger.warning(
            "OpenAI adapter is a placeholder and not yet implemented"
        )

    def generate(self, request: LLMRequest) -> LLMResponse:
        """
        Generate a response from the LLM.

        Args:
            request: The LLM request

        Returns:
            LLMResponse with generated content

        Raises:
            LLMServiceError: Always raises - not implemented
        """
        raise LLMServiceError(
            "OpenAI adapter is not yet implemented",
            details={"provider": "openai", "status": "placeholder"}
        )

    def health_check(self) -> bool:
        """
        Check if the LLM service is healthy.

        Returns:
            False - not implemented
        """
        logger.warning("OpenAI health check called but not implemented")
        return False
