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
            "You are Alfred, a helpful and concise assistant. Keep your responses brief and "
            "to the point, typically 1-3 sentences unless more detail is specifically requested."
        )

    def _build_system_message(self, thread_id: int) -> LLMMessage:
        context = self.chat_service.build_thread_context(thread_id)
        content = self.base_system_prompt
        if context:
            content = f"{content}\n\nThread context:\n{context}"
        return LLMMessage(role=LLMMessageRole.SYSTEM, content=content)

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
            user_id: User ID for session association
            thread_id: Thread ID for context association
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature (0.0 to 2.0)

        Returns:
            Structured LLMResponseDTO with AI response

        Raises:
            RuntimeError: If LLM service fails
        """

        if thread_id is None:
            raise ValueError("thread_id is required for chat context.")

        chat_session = self.chat_service.get_or_create_session(user_id, thread_id)
        if chat_session.id is None:
            raise ValueError("Failed to resolve chat session ID.")

        history = self.chat_service.get_session_messages(chat_session.id)
        conversation_history = [
            self._build_system_message(thread_id),
            *[LLMMessage(role=msg.role, content=msg.content) for msg in history],
        ]

        completion_response = self.service.generate_completion_with_history(
            prompt=prompt,
            conversation_history=conversation_history,
            max_tokens=max_tokens or self.service.default_max_tokens,
            temperature=temperature or self.service.default_temperature,
        )

        response_text = completion_response.completion_text
        self.chat_service.save_message(chat_session.id, LLMMessageRole.USER, prompt)
        self.chat_service.save_message(chat_session.id, LLMMessageRole.ASSISTANT, response_text)

        return LLMResponseDTO.from_completion_text(response_text)
