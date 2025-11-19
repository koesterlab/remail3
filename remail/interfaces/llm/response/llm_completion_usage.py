"""LLM completion usage dataclass."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(slots=True)
class LLMCompletionUsage:
    """Token accounting for the completion request."""

    prompt_tokens: int | None = None
    completion_tokens: int | None = None
    total_tokens: int | None = None
    prompt_tokens_details: dict[str, Any] | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any] | None) -> LLMCompletionUsage | None:
        """Create a usage instance from an API response dictionary."""

        if not isinstance(data, dict):
            return None

        return cls(
            prompt_tokens=data.get("prompt_tokens"),
            completion_tokens=data.get("completion_tokens"),
            total_tokens=data.get("total_tokens"),
            prompt_tokens_details=data.get("prompt_tokens_details"),
        )
