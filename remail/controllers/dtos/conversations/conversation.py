from dataclasses import dataclass

from .contact import ContactDTO
from .thread_preview import ThreadPreviewDTO


@dataclass
class ConversationDTO:
    contacts: list[ContactDTO]
    threads: list[ThreadPreviewDTO]
    is_favorite: bool
    customName: str | None
