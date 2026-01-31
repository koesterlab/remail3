from dataclasses import dataclass

from remail.enums import ContactType
from remail.models import Contact

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

    @classmethod
    def from_model(cls, contact: Contact):
        return ContactDTO(
            id=contact.id or -1,
            first_name=contact.first_name or "",
            last_name=contact.last_name or contact.name or "",
            email=contact.email_address,
            is_known=contact.is_known,
            type=contact.contact_type,
        )
