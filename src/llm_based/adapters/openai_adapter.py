"""
OpenAI adapter for LLM operations.

Implements the ILLMProvider interface for OpenAI models.
"""

from typing import Optional
from langchain_openai import ChatOpenAI

from src.llm_based.core.interfaces import ILLMProvider
from src.llm_based.core.models import LLMRequest, LLMResponse
from src.llm_based.core.exceptions import LLMServiceError, LLMTimeoutError
from src.llm_based.config.settings import settings
from src.llm_based.utils.logger import get_logger

logger = get_logger(__name__)


class OpenAIAdapter(ILLMProvider):
    """
    OpenAI implementation of ILLMProvider.

    This is a placeholder for future implementation.
    """

    def __init__(
        self,
        model_name: str = "gpt-3.5-turbo",
        api_key: Optional[str] = None,
    ):
        """
        Initialize OpenAI adapter.

        Args:
            model_name: OpenAI model name
            api_key: OpenAI API key
        """
        self.model_name = model_name
        self.api_key = api_key

        logger.warning(
            "OpenAI adapter is a placeholder and not yet implemented",
            model=model_name
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

    def get_provider_name(self) -> str:
        """
        Get the name of the LLM provider.

        Returns:
            Provider name
        """
        return "openai"


# TODO: Future implementation outline
#
# class OpenAIAdapter(ILLMProvider):
#     """OpenAI implementation using OpenAI SDK."""
#
#     def __init__(self, model_name: str = "gpt-3.5-turbo", api_key: Optional[str] = None):
#         from openai import OpenAI
#
#         self.model_name = model_name
#         self.client = OpenAI(api_key=api_key)
#
#     def generate(self, request: LLMRequest) -> LLMResponse:
#         full_prompt = request.prompt.format(resume=request.context, attribute=request.attribute)
#
#         response = self.client.chat.completions.create(
#             model=self.model_name,
#             messages=[
#                 {"role": "system", "content": "You are an expert resume parser."},
#                 {"role": "user", "content": full_prompt}
#             ],
#             temperature=request.temperature or 0.1,
#             max_tokens=request.max_tokens or 2048,
#         )
#
#         return LLMResponse(
#             content=response.choices[0].message.content,
#             attribute=request.attribute,
#             model_name=self.model_name,
#             tokens_used=response.usage.total_tokens,
#         )
