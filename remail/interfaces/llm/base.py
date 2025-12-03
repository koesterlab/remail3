"""Base class for LLM services."""

from abc import ABC, abstractmethod
from typing import Any

from remail.interfaces.llm.dto import LLMMessage
from remail.interfaces.llm.response import LLMCompletionResponse


class LLMBase(ABC):
    """Abstract base class for LLM service implementations."""

    @abstractmethod
    def generate_completion(
        self,
        prompt: str,
        max_tokens: int | None = None,
        temperature: float | None = None,
        **kwargs: Any,
    ) -> LLMCompletionResponse:
        """
        Generate text completion from prompt.

        Args:
            prompt: Input prompt for the LLM
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature (0.0 to 2.0)
            **kwargs: Additional provider-specific parameters

        Returns:
            Structured LLM completion response
        """

        pass

    @abstractmethod
    def generate_completion_with_history(
        self,
        prompt: str,
        conversation_history: list[LLMMessage],
        max_tokens: int | None = None,
        temperature: float | None = None,
        **kwargs: Any,
    ) -> LLMCompletionResponse:
        """
        Generate text completion with conversation history.

        Args:
            prompt: Input prompt for the LLM
            conversation_history: List of previous messages in the conversation
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature (0.0 to 2.0)
            **kwargs: Additional provider-specific parameters

        Returns:
            Structured LLM completion response
        """

        pass
