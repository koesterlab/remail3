from enum import Enum


class RecipientKind(Enum):
    TO = "to"
    CC = "cc"
    BCC = "bcc"


__all__ = ["RecipientKind"]
