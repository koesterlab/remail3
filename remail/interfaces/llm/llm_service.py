"""LLM service implementation."""

from __future__ import annotations

import os
from typing import Any

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
        if not self.api_key:
            raise ValueError("LLM_API_KEY environment variable is required")

        self.base_url = os.getenv("LLM_BASE_URL")
        if not self.base_url:
            raise ValueError("LLM_BASE_URL environment variable is required")

        self.model = LLMModel.META_LLAMA_3_1_8B_INSTRUCT
        self.default_max_tokens = 768
        self.default_temperature = 0.7
        self.default_top_p = 1.0

        self.client = self._init_client()

    def _init_client(self) -> OpenAI:
        """Initialize the OpenAI client."""

        return OpenAI(
            api_key=self.api_key,
            base_url=self.base_url,
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
                content="You are a helpful assistant. You must always return a JSON response.",
            ),
            LLMMessage(role=LLMMessageRole.USER, content=prompt),
        ]

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
            raise RuntimeError(f"OpenAI completion failed: {str(e)}") from e
