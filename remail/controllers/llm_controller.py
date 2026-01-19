"""LLM controller for managing LLM operations."""

from __future__ import annotations

from typing import Any

from remail.controllers.dtos import LLMResponseDTO
from remail.interfaces.llm.chat_service import ChatService
from remail.interfaces.llm.dto import LLMMessage
from remail.interfaces.llm.enums.llm_message_role import LLMMessageRole
from remail.interfaces.llm.llm_service import _BASE_SYSTEM_PROMPT as LLM_BASE_SYSTEM_PROMPT
from remail.interfaces.llm.llm_service import LLMService


class LLMController:
    """Controller for LLM operations."""

    _BASE_SYSTEM_PROMPT = LLM_BASE_SYSTEM_PROMPT

    def __init__(self) -> None:
        """Initialize LLM controller."""

        self.service = LLMService()
        self.chat_service = ChatService()

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
        user_id: int,
        thread_id: int,
        max_tokens: int | None = None,
        temperature: float | None = None,
    ) -> LLMResponseDTO:
        """
        Generate chat response with conversation history.

        Args:
            prompt: User's message
            user_id: ID of the active user
            thread_id: ID of the active thread
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature (0.0 to 2.0)

        Returns:
            Structured LLMResponseDTO with AI response

        Raises:
            RuntimeError: If LLM service fails
        """

        chat_session = self.chat_service.get_or_create_session(user_id, thread_id)
        if chat_session.id is None:
            raise ValueError("Chat session ID cannot be None")
        session_id = chat_session.id
        thread_context = self.chat_service.build_thread_context(thread_id)
        system_msg = self._build_system_message(thread_context)

        conversation_history = [
            system_msg,
            *self.chat_service.get_session_messages(session_id),
        ]

        # Generate response using conversation history + thread context
        completion_response = self.service.generate_completion_with_history(
            prompt=prompt,
            conversation_history=conversation_history,
            max_tokens=max_tokens or self.service.default_max_tokens,
            temperature=temperature or self.service.default_temperature,
        )

        # Extract response text
        response_text = completion_response.completion_text

        self.chat_service.save_message(session_id, LLMMessageRole.USER, prompt)
        self.chat_service.save_message(session_id, LLMMessageRole.ASSISTANT, response_text)

        return LLMResponseDTO.from_completion_text(response_text)

    def get_session_messages(self, user_id: int, thread_id: int) -> list[LLMMessage]:
        """
        Fetch saved chat messages for a user and thread.

        Args:
            user_id: ID of the active user
            thread_id: ID of the active thread

        Returns:
            List of LLMMessage instances
        """

        chat_session = self.chat_service.get_or_create_session(user_id, thread_id)
        if chat_session.id is None:
            raise ValueError("Chat session ID cannot be None")
        return self.chat_service.get_session_messages(chat_session.id)

    def reset_chat_memory(self, user_id: int, thread_id: int) -> None:
        """Clear chat history for a user and thread."""

        chat_session = self.chat_service.get_or_create_session(user_id, thread_id)
        if chat_session.id is None:
            raise ValueError("Chat session ID cannot be None")
        self.chat_service.clear_session_messages(chat_session.id)

    def _build_system_message(self, thread_context: str) -> LLMMessage:
        if not thread_context:
            return LLMMessage(role=LLMMessageRole.SYSTEM, content=self._BASE_SYSTEM_PROMPT)

        content = (
            f"{self._BASE_SYSTEM_PROMPT}\n\n"
            "Use the email thread context below to answer questions. "
            "If the answer is not in the thread, say you do not know.\n\n"
            f"{thread_context}"
        )
        return LLMMessage(role=LLMMessageRole.SYSTEM, content=content)
