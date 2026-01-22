"""LLM controller for managing LLM operations."""

from __future__ import annotations

from typing import Any

from remail.controllers.dtos import LLMResponseDTO
from remail.interfaces.llm.chat_service import ChatService
from remail.interfaces.llm.dto import LLMMessage
from remail.interfaces.llm.enums.llm_message_role import LLMMessageRole
from remail.interfaces.llm.llm_service import LLMService


class LLMController:
    """Controller for LLM operations."""

    def __init__(self) -> None:
        """Initialize LLM controller."""

        self.service = LLMService()
        self.chat_service = ChatService()
        self.base_system_prompt = (
            "You are Alfred, a helpful and concise assistant. "
            "Keep your responses brief and to the point, typically 1-3 sentences "
            "unless more detail is specifically requested."
        )

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
        thread_id: int,
        user_id: int,
        max_tokens: int | None = None,
        temperature: float | None = None,
    ) -> LLMResponseDTO:
        """
        Generate chat response with conversation history.

        Args:
            prompt: User's message
            thread_id: Thread ID used for context and persistence
            user_id: User ID used for session lookup
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature (0.0 to 2.0)

        Returns:
            Structured LLMResponseDTO with AI response

        Raises:
            RuntimeError: If LLM service fails
        """

        session = self.chat_service.get_or_create_session(user_id=user_id, thread_id=thread_id)
        if session.id is None:
            raise ValueError("Chat session ID cannot be None")
        history_messages = self.chat_service.get_session_messages(session.id)
        conversation_history = [
            LLMMessage(role=message.role, content=message.content)
            for message in history_messages
        ]

        system_prompt = self._build_system_prompt(thread_id)

        # Generate response using conversation history
        completion_response = self.service.generate_completion_with_history(
            prompt=prompt,
            conversation_history=conversation_history,
            max_tokens=max_tokens or self.service.default_max_tokens,
            temperature=temperature or self.service.default_temperature,
            system_prompt=system_prompt,
        )

        # Extract response text
        response_text = completion_response.completion_text

        # Persist user and assistant messages
        self.chat_service.save_message(session_id=session.id, role=LLMMessageRole.USER, content=prompt)
        self.chat_service.save_message(
            session_id=session.id,
            role=LLMMessageRole.ASSISTANT,
            content=response_text,
        )

        return LLMResponseDTO.from_completion_text(response_text)

    def get_session_messages(self, user_id: int, thread_id: int) -> list[LLMMessage]:
        """Fetch persisted chat messages for a user/thread session."""
        session = self.chat_service.get_or_create_session(user_id=user_id, thread_id=thread_id)
        if session.id is None:
            raise ValueError("Chat session ID cannot be None")
        history_messages = self.chat_service.get_session_messages(session.id)
        return [LLMMessage(role=message.role, content=message.content) for message in history_messages]

    def reset_chat_memory(self) -> None:
        """Reset chat memory (no-op for persisted sessions)."""

        return None

    def _build_system_prompt(self, thread_id: int) -> str:
        thread_context = self.chat_service.build_thread_context(thread_id)
        if not thread_context:
            return self.base_system_prompt

        return f"{self.base_system_prompt}\n\nThread context:\n{thread_context}"
