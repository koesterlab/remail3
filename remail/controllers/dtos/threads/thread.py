from dataclasses import dataclass

from .message import MessageDTO


@dataclass
class ThreadDTO:
    id: int
    title: str
    messages: list[MessageDTO]
