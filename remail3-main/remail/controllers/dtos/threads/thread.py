from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from remail.models import Thread

if TYPE_CHECKING:
    from ..conversations import ContactDTO

from .message import MessageDTO


@dataclass
class ThreadDTO:
    id: int
    title: str
    messages: list[MessageDTO]
    contacts: list["ContactDTO"] = field(default_factory=list)

    @staticmethod
    def from_model(thread: Thread) -> "ThreadDTO":
        return ThreadDTO(
            id=thread.id if thread.id else -1,
            title=thread.title,
            messages=[MessageDTO.from_model(m) for m in thread.messages],
        )
