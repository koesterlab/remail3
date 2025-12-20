from dataclasses import dataclass

from remail.controllers.dtos.threads import SenderDTO
from remail.enums import ContactType


@dataclass
class ContactDTO(SenderDTO):
    is_known: bool
    type: ContactType

    def __eq__(self, other):
        return isinstance(other, ContactDTO) and other.id == self.id
