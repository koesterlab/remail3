"""LLM service implementation."""

from __future__ import annotations

import os
from typing import Any

from llama_index.llms.openai_like import OpenAILike
from openai import OpenAI

from remail.interfaces.llm.base import LLMBase
from remail.interfaces.llm.dto import LLMMessage
from remail.interfaces.llm.enums.llm_message_role import LLMMessageRole
from remail.interfaces.llm.enums.llm_model import LLMModel
from remail.interfaces.llm.response import LLMCompletionResponse


class LLMService(LLMBase):
    """LLM service implementation using OpenAI client."""

    def __init__(self):
        """Initialize LLM service."""

        self.api_key = os.getenv("LLM_API_KEY")
        self.api_key = "3fac3a411f572bfc755ea43b7f04d6d5" #todo: REMOVE BEFORE PUSH!!!
        if not self.api_key:
            raise ValueError("LLM_API_KEY environment variable is required")

        self.base_url = os.getenv("LLM_BASE_URL")
        self.base_url = "https://chat-ai.academiccloud.de/v1" #todo: REMOVE BEFORE PUSH!!!
        if not self.base_url:
            raise ValueError("LLM_BASE_URL environment variable is required")

        self.model = LLMModel.META_LLAMA_3_1_8B_INSTRUCT
        self.default_max_tokens = 150
        self.default_temperature = 0.7
        self.default_top_p = 1.0

        self.client = self._init_client()
        self.llama_llm = self._init_llama_llm()

    def _init_client(self) -> OpenAI:
        """Initialize the OpenAI client."""

        return OpenAI(
            api_key=self.api_key,
            base_url=self.base_url,
        )

    def _init_llama_llm(self) -> OpenAILike:
        """Initialize LlamaIndex OpenAI-compatible LLM."""

        return OpenAILike(
            model=self.model.value,
            api_key=self.api_key,
            api_base=self.base_url,
            max_tokens=self.default_max_tokens,
            temperature=self.default_temperature,
        )

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
            LLMMessage(role=LLMMessageRole.USER, content=prompt),
        ]

        return self._generate_completion_internal(messages, max_tokens, temperature, **kwargs)

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
                model=self.model.value,
                messages=[msg.to_dict() for msg in messages],
                max_tokens=max_tokens or self.default_max_tokens,
                temperature=temperature or self.default_temperature,
                top_p=kwargs.get("top_p", self.default_top_p),
            )

            data = response.model_dump()

            return LLMCompletionResponse.from_dict(data)

        except Exception as e:
            raise RuntimeError(f"LLM completion failed: {str(e)}") from e
