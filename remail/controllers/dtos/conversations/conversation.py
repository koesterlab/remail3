from dataclasses import dataclass

from .contact import ContactDTO
from .thread_preview import ThreadPreviewDTO


@dataclass()
class ConversationDTO:
    contacts: list[ContactDTO]
    threads: list[ThreadPreviewDTO]
    is_favorite: bool
    customName: str | None

    def __hash__(self):
        return hash(tuple(self.contacts))

    def get_member_string(self):
        return ", ".join([c.first_name[0] + ". " + c.last_name for c in self.contacts])
