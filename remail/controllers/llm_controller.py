"""LLM controller for managing LLM operations."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from remail.controllers.dtos import LLMResponseDTO
from remail.interfaces.llm.dto import LLMMessage
from remail.interfaces.llm.enums.llm_message_role import LLMMessageRole
from remail.interfaces.llm.llm_service import LLMService
from remail.interfaces.llm.services import ChatService

if TYPE_CHECKING:
    from sqlmodel import Session


class LLMController:
    """Controller for LLM operations."""

    def __init__(self, db_session: Session | None = None):
        """Initialize LLM controller.

        Args:
            db_session: Optional database session for chat persistence
        """

        self.service = LLMService()
        self.conversation_history: list[LLMMessage] = []

        system_msg = LLMMessage(
            role=LLMMessageRole.SYSTEM,
            content="You are Alfred, a helpful and concise assistant. Keep your responses brief and to the point, typically 1-3 sentences unless more detail is specifically requested.",
        )

        self.conversation_history.append(system_msg)
        # Lazy load LLMService to allow environment patches in tests
        self._service = None
        self.db_session = db_session
        self.chat_service = ChatService(db_session) if db_session else None

    @property
    def service(self):
        """Lazy load LLM service on first access."""
        if self._service is None:
            from remail.interfaces.llm.llm_service import LLMService
            self._service = LLMService()
        return self._service

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

    def chat_with_thread_context(
        self,
        user_id: int,
        thread_id: int,
        user_message: str,
        system_prompt: str | None = None,
        max_tokens: int | None = None,
        temperature: float | None = None,
    ) -> dict[str, Any]:
        """
        Generate chat response with thread context and persistence.

        Args:
            user_id: ID of the user
            thread_id: ID of the email thread to use as context
            user_message: User's message
            system_prompt: Optional custom system prompt
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature

        Returns:
            Dict with status, message, session_id, and response
        """
        if not self.chat_service:
            return {
                "status": "error",
                "message": "Chat service not available (no database session)",
            }

        try:
            # Get or create session
            session = self.chat_service.get_or_create_session(user_id, thread_id)

            # Build thread context
            thread_context = self.chat_service.build_thread_context(thread_id)

            # Save user message
            self.chat_service.save_message(session.id, "user", user_message)

            # Build messages for LLM
            messages = self.chat_service.get_session_messages(session.id)
            formatted_messages = [
                {"role": msg.role, "content": msg.content} for msg in messages
            ]

            # Construct final prompt with thread context
            final_prompt = user_message
            if thread_context:
                final_prompt = f"{thread_context}\n\nUser query: {user_message}"

            if system_prompt is None:
                system_prompt = "You are a helpful email assistant. Use the provided email thread context to answer user questions."

            # Add system message if not already present
            if not formatted_messages or formatted_messages[0]["role"] != "system":
                formatted_messages.insert(0, {"role": "system", "content": system_prompt})

            # Generate completion
            completion_response = self.service.generate_completion(
                prompt=final_prompt,
                max_tokens=max_tokens,
                temperature=temperature,
            )

            assistant_message = completion_response.completion_text

            # Save assistant message
            self.chat_service.save_message(session.id, "assistant", assistant_message)

            # Update session timestamp
            self.chat_service.update_session_timestamp(session.id)

            return {
                "status": "success",
                "message": "Chat response generated successfully",
                "session_id": session.id,
                "completion": assistant_message,
                "response": completion_response,
            }

        except Exception as e:
            return {
                "status": "error",
                "message": f"Chat generation failed: {str(e)}",
            }

