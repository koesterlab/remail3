from enum import Enum


class ConversationType(str, Enum):
    CONVERSATION = "conversation"
    GROUP = "group"


__all__ = ["ConversationType"]
