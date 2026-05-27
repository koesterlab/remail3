from enum import Enum, auto


class Protocol(Enum):
    IMAP = auto()
    EXCHANGE = auto()


__all__ = ["Protocol"]
