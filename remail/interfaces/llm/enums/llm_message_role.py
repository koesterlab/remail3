import enum


class LLMMessageRole(enum.Enum):
    """Message role types in LLM conversations."""

    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"
