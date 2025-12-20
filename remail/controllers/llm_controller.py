"""LLM controller for managing LLM operations."""

from __future__ import annotations

from typing import Any

from remail.controllers.dtos import LLMResponseDTO
from remail.interfaces.llm.dto import LLMMessage
from remail.interfaces.llm.enums.llm_message_role import LLMMessageRole
from remail.interfaces.llm.llm_service import LLMService



class LLMController:
    """Controller for LLM operations."""

    def __init__(self, ) -> None:
        """Initialize LLM controller."""

        self.service = LLMService()
        self.conversation_history: list[LLMMessage] = []

        system_msg = LLMMessage(
            role=LLMMessageRole.SYSTEM,
            content="""
Your name is AIfred. You are the assistant of an email application. Your task is to proceed user requests.
The emails are grouped in Conversations (same Recipients) and Threads (same Recipients and Subject)
You have a number of possibilities to serve the user, output the command to get input or do actions. multiple lines means multiple prompts.:
/say [message] - output text to user
/getDraft - you get the current email-draft of the user
/setDraft [draft_content] - set the content of the email-draft
/getCurrentThread - you get the current thread the user is viewing, eg to get context to a draft 
!any unannotated lines will be ignored. if you need multiline, use \\n!
"""
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

        # Add user messages to history
        user_msg = LLMMessage(role=LLMMessageRole.USER, content=prompt)
        self.conversation_history.append(user_msg)

        next_input = prompt #providing new content until the llm says its finished
        text_outputs = [] #output that is displayed in chat
        local_history: list[LLMMessage] = [] #context for the currrent command
        saved_history: list[LLMMessage] = [] #context saved for future commands

        self.conversation_history += saved_history

        return LLMResponseDTO.from_completion_text("\n".join(text_outputs))

    def reset_chat_memory(self) -> None:
        """Reset the chat memory to start a fresh conversation."""

        self.conversation_history = []

        system_msg = LLMMessage(
            role=LLMMessageRole.SYSTEM,
            content="You are Alfred, a helpful and concise assistant. Keep your responses brief and to the point, typically 1-3 sentences unless more detail is specifically requested.",
        )

        self.conversation_history.append(system_msg)
