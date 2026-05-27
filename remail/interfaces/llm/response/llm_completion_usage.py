from dataclasses import dataclass
from typing import Any


@dataclass(slots=True)
class LLMCompletionUsage:
    prompt_tokens: int | None = None  # vulture: ignore
    completion_tokens: int | None = None  # vulture: ignore
    total_tokens: int | None = None  # vulture: ignore
    prompt_tokens_details: dict[str, Any] | None = None  # vulture: ignore

    @classmethod
    def from_dict(cls, data: dict[str, Any] | None) -> "LLMCompletionUsage | None":
        if not isinstance(data, dict):
            return None

        return cls(
            prompt_tokens=data.get("prompt_tokens"),
            completion_tokens=data.get("completion_tokens"),
            total_tokens=data.get("total_tokens"),
            prompt_tokens_details=data.get("prompt_tokens_details"),
        )
