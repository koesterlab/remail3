from dataclasses import dataclass, field
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..conversations import ContactDTO

from .message import MessageDTO


@dataclass
class ThreadDTO:
    id: int
    title: str
    messages: list[MessageDTO]
    contacts: list["ContactDTO"] = field(default_factory=list)
