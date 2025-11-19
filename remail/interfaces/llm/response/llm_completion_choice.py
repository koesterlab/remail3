"""LLM completion choice dataclass."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from remail.interfaces.llm.response.llm_completion_message import LLMCompletionMessage


@dataclass(slots=True)
class LLMCompletionChoice:
    """A single model choice inside the completion response."""

    index: int
    message: LLMCompletionMessage | None = None
    finish_reason: str | None = None
    stop_reason: str | None = None
    logprobs: dict[str, Any] | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> LLMCompletionChoice:
        """Create a choice instance from an API response dictionary."""

        message = data.get("message")

        return cls(
            index=int(data.get("index", 0)),
            message=LLMCompletionMessage.from_dict(message) if isinstance(message, dict) else None,
            finish_reason=data.get("finish_reason"),
            stop_reason=data.get("stop_reason"),
            logprobs=data.get("logprobs"),
        )

    @property
    def message_text(self) -> str:
        """Return the textual content of the message, if available."""

        if not self.message:
            return ""

        content = self.message.content

        if isinstance(content, str):
            return content

        if isinstance(content, list):
            return "".join(str(part) for part in content)

        if content is None:
            return ""

        return str(content)
