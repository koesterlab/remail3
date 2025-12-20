"""LLM controller for managing LLM operations."""

from __future__ import annotations

import re
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
You are AIfred, the assistant of an email application.

Your task is to fulfill user requests by ONLY outputting valid commands.
Do NOT output explanations, comments, or natural language outside commands.
Do not request permission manually and use the different types of interaction

If you get a new request, follow these steps:
1. Identify which action the user wants you to do
2. use information-retrieving commands to get more context. Finish your response and wait for the data
3. generate the output for the user
4. think about the best way to pass the generated data to the user, e.g. /say or /setDraft

Rules:
- Every response MUST consist of one or more commands.
- Make sure to escape non-command-"/" in your text with "\\/".
- Any text not starting with a command will be ignored.
- Do NOT set or modify the draft unless you have first retrieved the necessary context with the other commands
- If the required information is missing, do not take actions, but instead retrieve information with the other commands
- Use multiple command lines if needed.
- If information is missing, ask the user using /say.
- Use /getDraft or /getCurrentThread only when useful to fulfill the request.
- Always pass new mails to draft section with /setDraft, never use /say for them, only to ask for confirmation
- Pass emails as text, no formatting, no subject. Pay attention to correct line breaks

Available commands:
/say [message]            - send a message to the user
/getDraft                 - retrieve the current email draft. only use it once per command
/setDraft [draft_content] - replace the entire email draft (for the current active thread). Use this every time a user wants to write an email, to show your email to the user. Only use this if you have enough information to write the mail
/getCurrentThread         - retrieve the currently viewed thread for context. only use it once per user command



Information about the User. He is the one you are writing and reading mails as. You act as him:
name: Jonathan Dreisvogt
email: jonathan.dreisvogt@outlook.de
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

        print("---> Prompt: " + prompt)

        # loop through responses until ai agent is finished
        while next_input != "":
            # Generate response using conversation history
            completion_response = self.service.generate_completion_with_history(
                prompt=next_input,
                conversation_history=self.conversation_history,
                max_tokens=max_tokens or self.service.default_max_tokens,
                temperature=temperature or self.service.default_temperature,
            )
            # reset input
            next_input = ""
            # Extract response commands
            print("Complete output: " + completion_response.completion_text + " end of output" )
            print(re.split(r'(?<!\\)/', completion_response.completion_text))
            for command in re.split(r'(?<!\\)/', completion_response.completion_text)[1:]:
                words:list[str] = command.split()
                words = [w.replace("\\n", "\n").replace("\\/", "/") for w in words]
                params = words[1:]
                match words[0].strip():
                    case "say":
                        print("-Outputting Text")
                        message = LLMMessage(role=LLMMessageRole.SYSTEM, content=" ".join(params))
                        text_outputs.append(message.content)
                        self.conversation_history.append(message)
                        self.conversation_history.append(message)
                    case "getDraft":
                        print("-Sending Draft")
                        content = "Current Draft: " + self.frontend_state.get(MainAppStateProperties.DRAFT) + "\n"
                        next_input += content
                        self.conversation_history.append(LLMMessage(role=LLMMessageRole.DATA, content=content))
                    case "getCurrentThread":
                        print("-Sending Thread Info")
                        thread:ThreadPreviewDTO = self.frontend_state.get(MainAppStateProperties.ACTIVE_THREAD)
                        full_thread: ThreadDTO = fetch_thread(thread)  # todo
                        content = ("Subject:" + full_thread.title + "\n" + "\n".join(
                                           msg.sender.first_name + " " + msg.sender.last_name + ": " + msg.content.body for
                                           msg in full_thread.messages) + "\n\n")
                        print(content)
                        next_input += content
                        self.conversation_history.append(LLMMessage(role=LLMMessageRole.DATA, content=content))
                    case "setDraft":
                        print("-Setting Draft")
                        message = " ".join(params)
                        self.frontend_state.set(MainAppStateProperties.DRAFT, message)
                        self.conversation_history.append(LLMMessage(role=LLMMessageRole.COMMAND, content="New Draft: " + message))

        return LLMResponseDTO.from_completion_text("\n".join(text_outputs))

    def reset_chat_memory(self) -> None:
        """Reset the chat memory to start a fresh conversation."""

        self.conversation_history = []

        system_msg = LLMMessage(
            role=LLMMessageRole.SYSTEM,
            content="You are Alfred, a helpful and concise assistant. Keep your responses brief and to the point, typically 1-3 sentences unless more detail is specifically requested.",
        )

        self.conversation_history.append(system_msg)
