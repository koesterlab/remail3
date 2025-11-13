from typing import TYPE_CHECKING

import sqlalchemy
from sqlmodel import Field, Relationship, SQLModel

from remail.enums import RecipientKind

# Import at runtime so SA can resolve the targets
from .contact import Contact  # noqa: F401
from .email import Email  # noqa: F401

if TYPE_CHECKING:
    pass


class EmailReception(SQLModel, table=True):
    __tablename__ = "email_receptions"

    kind: RecipientKind = Field(
        sa_column=sqlalchemy.Column(sqlalchemy.Enum(RecipientKind), nullable=False)
    )
    email_id: int = Field(foreign_key="emails.id", primary_key=True)
    contact_id: int = Field(foreign_key="contacts.id", primary_key=True)

    email: Email = Relationship(back_populates="recipients")
    contact: Contact = Relationship(back_populates="receptions")
