"""Message dataclass for LLM requests."""

from __future__ import annotations

from dataclasses import dataclass

from remail.interfaces.llm.enums.llm_message_role import LLMMessageRole


@dataclass(slots=True)
class LLMMessage:
    """A message in an LLM conversation."""

    role: LLMMessageRole
    content: str

    def to_dict(self) -> dict[str, str]:
        """Convert message to API-compatible dictionary."""

        return {
            "role": self.role.value,
            "content": self.content,
        }
