"""LLM controller for managing LLM operations."""

from __future__ import annotations

from typing import Any

from remail.client.state import MainAppState, MainAppStateProperties
from remail.controllers.dtos import LLMResponseDTO
from remail.controllers.dtos.threads import ThreadDTO
from remail.interfaces.llm.dto import LLMMessage
from remail.interfaces.llm.enums.llm_message_role import LLMMessageRole
from remail.interfaces.llm.llm_service import LLMService
from tests import fetch_thread
from tests.client.state.test_main_app_state import ThreadPreviewDTO


class ChatPromptManager:
    """Controller for LLM operations."""

    def __init__(self, state: MainAppState) -> None:
        """Initialize LLM controller."""

        self.service = LLMService()
        self.frontend_state = state
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

        # loop through responses until ai agent is finished
        while next_input != "":
            # Generate response using conversation history
            completion_response = self.service.generate_completion_with_history(
                prompt=next_input,
                conversation_history=self.conversation_history + local_history,
                max_tokens=max_tokens or self.service.default_max_tokens,
                temperature=temperature or self.service.default_temperature,
            )
            # reset input
            next_input = ""
            # Extract response commands
            errors = 0
            for command in completion_response.completion_text.splitlines():
                if not command.startswith("/"):
                    errors += 1
                    continue
                words = command.split()
                params = words[1:]
                match words[0][1:]:
                    case "say":
                        message = LLMMessage(role=LLMMessageRole.SYSTEM, content=" ".join(params))
                        text_outputs.append(message.content)
                        local_history.append(message)
                        saved_history.append(message)
                    case "getDraft":
                        content = "Current Draft: " + self.frontend_state.get(MainAppStateProperties.DRAFT) + "\n"
                        next_input += content
                        local_history.append(LLMMessage(role=LLMMessageRole.DATA, content=content))
                    case "getCurrentThread":
                        thread:ThreadPreviewDTO = self.frontend_state.get(MainAppStateProperties.ACTIVE_THREAD)
                        full_thread: ThreadDTO = fetch_thread(thread)  # todo
                        content = ("Subject:" + thread.subject + "\n" + "\n".join(
                                           msg.sender.first_name + " " + msg.sender.last_name + ": " + msg.content.body for
                                           msg in full_thread.messages) + "\n\n")
                        next_input += content
                        local_history.append(LLMMessage(role=LLMMessageRole.DATA, content=content))
                    case "setDraft":
                        message = " ".join(params)
                        self.frontend_state.set(MainAppStateProperties.DRAFT, message)
                        local_history.append(LLMMessage(role=LLMMessageRole.COMMAND, content="New Draft: " + message))

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
