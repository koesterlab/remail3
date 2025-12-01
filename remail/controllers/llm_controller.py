"""LLM controller for managing LLM operations."""

from __future__ import annotations

from typing import Any

from remail.controllers.dto import LLMResponseDTO
from remail.interfaces.llm.dto import LLMMessage
from remail.interfaces.llm.enums.llm_message_role import LLMMessageRole
from remail.interfaces.llm.llm_service import LLMService


class LLMController:
    """Controller for LLM operations."""

    def __init__(self) -> None:
        """Initialize LLM controller."""

        self.service = LLMService()
        self.conversation_history: list[LLMMessage] = []

        system_msg = LLMMessage(
            role=LLMMessageRole.SYSTEM,
            content="You are Alfred, a helpful and concise assistant. Keep your responses brief and to the point, typically 1-3 sentences unless more detail is specifically requested.",
        )

        self.conversation_history.append(system_msg)

    def generate_completion(
        self,
        prompt: str,
        max_tokens: int | None = None,
        temperature: float | None = None,
        **kwargs: Any,
    ) -> LLMResponseDTO:
        """
        Generate text completion from prompt.

        Args:
            prompt: Input prompt for the LLM
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature (0.0 to 2.0)
            **kwargs: Additional provider-specific parameters

        Returns:
            Structured LLMResponseDTO

        Raises:
            ValueError: If response cannot be parsed
            RuntimeError: If LLM service fails
        """
        completion_response = self.service.generate_completion(
            prompt=prompt,
            max_tokens=max_tokens,
            temperature=temperature,
            **kwargs,
        )

        completion_text = completion_response.completion_text

        return LLMResponseDTO.from_completion_text(completion_text)

    def chat(
        self,
        prompt: str,
        max_tokens: int | None = None,
        temperature: float | None = None,
    ) -> LLMResponseDTO:
        """
        Generate chat response with conversation history.

        Args:
            prompt: User's message
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature (0.0 to 2.0)

        Returns:
            Structured LLMResponseDTO with AI response

        Raises:
            RuntimeError: If LLM service fails
        """

        # Generate response using conversation history
        completion_response = self.service.generate_completion_with_history(
            prompt=prompt,
            conversation_history=self.conversation_history,
            max_tokens=max_tokens or self.service.default_max_tokens,
            temperature=temperature or self.service.default_temperature,
        )

        # Extract response text
        response_text = completion_response.completion_text

        # Add user and assistant messages to history
        user_msg = LLMMessage(role=LLMMessageRole.USER, content=prompt)
        self.conversation_history.append(user_msg)

        assistant_msg = LLMMessage(role=LLMMessageRole.ASSISTANT, content=response_text)
        self.conversation_history.append(assistant_msg)

        return LLMResponseDTO.from_completion_text(response_text)

    def reset_chat_memory(self) -> None:
        """Reset the chat memory to start a fresh conversation."""

        self.conversation_history = []

        system_msg = LLMMessage(
            role=LLMMessageRole.SYSTEM,
            content="You are Alfred, a helpful and concise assistant. Keep your responses brief and to the point, typically 1-3 sentences unless more detail is specifically requested.",
        )

        self.conversation_history.append(system_msg)
