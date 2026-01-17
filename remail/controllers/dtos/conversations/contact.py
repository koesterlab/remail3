from dataclasses import dataclass

from remail.enums import ContactType

from ..threads import SenderDTO


@dataclass
class ContactDTO(SenderDTO):
    id: int
    first_name: str
    last_name: str
    email: str
    is_known: bool
    type: ContactType

    def __eq__(self, other):
        return isinstance(other, ContactDTO) and other.id == self.id

    def __hash__(self):
        return hash(self.id)
