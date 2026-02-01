from typing import TYPE_CHECKING

import sqlalchemy
from sqlmodel import Field, Relationship, SQLModel

from remail.enums import ContactType

# Import at runtime for SQLAlchemy
from .conversation_contact import ConversationContact  # noqa: F401

if TYPE_CHECKING:
    from .conversation import Conversation
    from .email import Email
    from .email_reception import EmailReception


class Contact(SQLModel, table=True):
    __tablename__ = "contacts"

    id: int | None = Field(default=None, primary_key=True)
    name: str
    email_address: str
    first_name: str | None = None
    last_name: str | None = None
    contact_type: ContactType = Field(
        default=ContactType.PRIVATE,
        sa_column=sqlalchemy.Column(sqlalchemy.Enum(ContactType), nullable=False),
    )
    is_known: bool = Field(
        default=False, description="Whether the contact is registered in our database"
    )

    receptions: list["EmailReception"] = Relationship(back_populates="contact")
    sent_emails: list["Email"] = Relationship(back_populates="sender")
    conversations: list["Conversation"] = Relationship(
        back_populates="contacts",
        link_model=ConversationContact,
    )

    def __eq__(self, other: object) -> bool:
        return isinstance(other, Contact) and other.email_address == self.email_address

    def __hash__(self) -> int:
        return hash(self.email_address)
