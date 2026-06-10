from remail.controllers.dtos import LLMResponseDTO
from remail.interfaces.llm.dto import LLMMessage
from remail.interfaces.llm.enums.llm_message_role import LLMMessageRole
from remail.interfaces.llm.llm_service import LLMService


class LLMController:
    """Controller for LLM operations."""

    def __init__(self, base_url: str, api_key: str) -> None:
        """Initialize LLM controller."""

        self.service = LLMService(base_url, api_key)
        self.conversation_history: list[LLMMessage] = []

        system_msg = LLMMessage(
            role=LLMMessageRole.SYSTEM,
            content="You are Alfred, a helpful and concise assistant. Keep your responses brief and to the point, typically 1-3 sentences unless more detail is specifically requested.",
        )

        self.conversation_history.append(system_msg)

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

        completion_response = self.service.generate_completion_with_history(
            prompt=prompt,
            conversation_history=self.conversation_history,
            max_tokens=max_tokens or self.service.default_max_tokens,
            temperature=temperature or self.service.default_temperature,
        )

        response_text = completion_response.completion_text
        user_msg = LLMMessage(role=LLMMessageRole.USER, content=prompt)

        self.conversation_history.append(user_msg)
        assistant_msg = LLMMessage(role=LLMMessageRole.ASSISTANT, content=response_text)
        self.conversation_history.append(assistant_msg)

        return LLMResponseDTO.from_completion_text(response_text)


    def generate_reply(
        self,
        email_body: str,
        max_tokens: int | None = None,
        temperature: float | None = None,
    ) -> LLMResponseDTO:
        """
        Generate a draft reply for a received email.

        Args:
            email_body: The body text of the email to reply to
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature (0.0 to 2.0)

        Returns:
            Structured LLMResponseDTO with the AI-generated draft reply
        """

        prompt = (
            "Write a polite and professional draft reply to the following email. "
            "Only return the reply text itself, without any extra explanation.\n\n"
            f"Email:\n{email_body}"
        )

        return self.chat(
            prompt=prompt,
            max_tokens=max_tokens,
            temperature=temperature,
        )