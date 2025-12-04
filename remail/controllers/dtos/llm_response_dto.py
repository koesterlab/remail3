"""Data class for LLM response with structured JSON format."""

from __future__ import annotations

import json
from dataclasses import dataclass


@dataclass(slots=True)
class LLMResponseDTO:
    """Structured DTO for LLM responses."""

    content: str

    @classmethod
    def from_completion_text(cls, text: str) -> LLMResponseDTO:
        """
        Parse LLM completion text into structured DTO.

        Args:
            text: The raw completion text from LLM (plain text)

        Returns:
            Parsed LLMResponseDTO
        """

        return cls(content=text.strip())

    def to_dict(self) -> dict[str, str]:
        """Convert DTO to dictionary."""

        return {"content": self.content}

    def to_json(self) -> str:
        """Convert DTO to JSON string."""

        return json.dumps(self.to_dict())
