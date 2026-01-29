from dataclasses import dataclass

from .contact import ContactDTO
from .thread_preview import ThreadPreviewDTO


@dataclass()
class ConversationDTO:
    id: int
    contacts: list[ContactDTO]
    threads: list[ThreadPreviewDTO]
    is_favorite: bool
    custom_name: str | None

    def __hash__(self):
        return hash(tuple(self.contacts))

    def get_member_string(self, extended: bool = False) -> str:
        def to_string(contact: ContactDTO) -> str:
            if contact.first_name and contact.last_name and len(contact.first_name) > 0:
                return (
                    (contact.first_name if extended else (contact.first_name[0] + "."))
                    + " "
                    + contact.last_name
                )
            elif contact.first_name:
                return contact.first_name
            elif contact.last_name:
                return contact.last_name
            else:
                return contact.email

        return ", ".join(to_string(c) for c in self.contacts)
