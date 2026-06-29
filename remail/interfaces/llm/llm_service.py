"""LLM service implementation."""

from __future__ import annotations

from typing import Any

from openai import OpenAI

from remail.interfaces.llm.base import LLMBase
from remail.interfaces.llm.dto import LLMMessage
from remail.interfaces.llm.enums.llm_message_role import LLMMessageRole
from remail.interfaces.llm.enums.llm_model import LLMModel
from remail.interfaces.llm.response import LLMCompletionResponse


class LLMService(LLMBase):
    """LLM service implementation using OpenAI client."""

    def __init__(self, base_url: str, api_key: str, model: str | None = None):
        """Initialize LLM service."""

        self.api_key = api_key
        self.base_url = base_url
        self.model = model or LLMModel.META_LLAMA_3_1_8B_INSTRUCT
        self.default_max_tokens = 150
        self.default_temperature = 0.7
        self.default_top_p = 1.0
        self.client = self._init_client()

    def _init_client(self) -> OpenAI:
        """Initialize the OpenAI client."""

        return OpenAI(
            api_key=self.api_key,
            base_url=self.base_url,
        )

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
            max_tokens: Optional override for maximum generated tokens
            temperature: Optional override for sampling temperature
            **kwargs: Additional parameters (e.g., top_p)

        Returns:
            Structured LLM completion response
        """

        messages = [
            LLMMessage(
                role=LLMMessageRole.SYSTEM,
                content="You are a helpful assistant. Your name is Alfred. Provide clear, concise, and helpful responses.",
            ),
            *conversation_history,
            LLMMessage(role=LLMMessageRole.USER, content=prompt),
        ]

        return self._generate_completion_internal(messages, max_tokens, temperature, **kwargs)

    def _generate_completion_internal(
        self,
        messages: list[LLMMessage],
        max_tokens: int | None = None,
        temperature: float | None = None,
        **kwargs: Any,
    ) -> LLMCompletionResponse:
        """
        Internal method to generate completion from messages.

        Args:
            messages: List of messages to send to the LLM
            max_tokens: Optional override for maximum generated tokens
            temperature: Optional override for sampling temperature
            **kwargs: Additional parameters (e.g., top_p)

        Returns:
            Structured LLM completion response
        """

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[msg.to_dict() for msg in messages],  # type:ignore
                max_tokens=max_tokens or self.default_max_tokens,
                temperature=temperature or self.default_temperature,
                top_p=kwargs.get("top_p", self.default_top_p),
            )

            data = response.model_dump()

            return LLMCompletionResponse.from_dict(data)

        except Exception as e:
            raise RuntimeError(f"LLM completion failed: {str(e)}") from e
