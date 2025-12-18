from dataclasses import dataclass, field

from remail.controllers.dtos.conversations import ContactDTO

from .message import MessageDTO


@dataclass
class ThreadDTO:
    id: int
    title: str
    messages: list[MessageDTO]
    contacts: list[ContactDTO] = field(default_factory=list)
