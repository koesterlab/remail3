from enum import StrEnum  # Enum yerine StrEnum import et


class ConversationType(StrEnum):  # (str, Enum) yerine sadece StrEnum kullan
    CONVERSATION = "conversation"
    GROUP = "group"
