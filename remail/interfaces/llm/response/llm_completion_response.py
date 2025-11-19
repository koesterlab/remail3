"""LLM completion response dataclass."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from remail.interfaces.llm.response.llm_completion_choice import LLMCompletionChoice
from remail.interfaces.llm.response.llm_completion_usage import LLMCompletionUsage


@dataclass(slots=True)
class LLMCompletionResponse:
    """Structured representation of the LLM completion HTTP response."""

    id: str
    object: str
    created: int
    model: str
    choices: list[LLMCompletionChoice] = field(default_factory=list)
    usage: LLMCompletionUsage | None = None
    service_tier: str | None = None
    system_fingerprint: str | None = None
    raw: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> LLMCompletionResponse:
        """Create a completion response from the provider payload."""

        choices_payload = data.get("choices") or []
        usage_payload = data.get("usage")

        return cls(
            id=str(data.get("id", "")),
            object=str(data.get("object", "")),
            created=int(data.get("created", 0)),
            model=str(data.get("model", "")),
            choices=[
                LLMCompletionChoice.from_dict(choice)
                for choice in choices_payload
                if isinstance(choice, dict)
            ],
            usage=LLMCompletionUsage.from_dict(usage_payload),
            service_tier=data.get("service_tier"),
            system_fingerprint=data.get("system_fingerprint"),
            raw=data,
        )

    @property
    def completion_text(self) -> str:
        """Return the first available choice text for convenience."""

        for choice in self.choices:
            text = choice.message_text

            if text:
                return text

        return ""

    def to_dict(self) -> dict[str, Any]:
        """Return the raw provider payload for serialization or logging."""

        return self.raw or {}
