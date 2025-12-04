from dataclasses import dataclass

from remail.enums import ContactType


@dataclass
class ContactDTO:
    id: int
    first_name: str
    last_name: str
    email: str
    is_known: bool
    type: ContactType
