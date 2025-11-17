"""LLM completion message dataclass."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from remail.interfaces.llm.enums.llm_message_role import LLMMessageRole


@dataclass(slots=True)
class LLMCompletionMessage:
    """Message payload returned within a completion choice."""

    role: LLMMessageRole
    content: Any
    refusal: str | None = None
    annotations: Any | None = None
    audio: Any | None = None
    function_call: dict[str, Any] | None = None
    tool_calls: list[dict[str, Any]] | None = None
    reasoning_content: Any | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> LLMCompletionMessage:
        """Create a message instance from an API response dictionary."""

        role_str = data.get("role", "assistant")

        try:
            role = LLMMessageRole(role_str)

        except ValueError:
            role = LLMMessageRole.ASSISTANT

        return cls(
            role=role,
            content=data.get("content"),
            refusal=data.get("refusal"),
            annotations=data.get("annotations"),
            audio=data.get("audio"),
            function_call=data.get("function_call"),
            tool_calls=data.get("tool_calls"),
            reasoning_content=data.get("reasoning_content"),
        )
