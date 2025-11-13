from datetime import datetime
from typing import TYPE_CHECKING

from sqlmodel import Field, Relationship, SQLModel

# Make target symbol available at runtime so SA can resolve it
from .contact import Contact  # noqa: F401

if TYPE_CHECKING:
    from .attachment import Attachment
    from .email_reception import EmailReception


class Email(SQLModel, table=True):
    __tablename__ = "emails"

    id: int | None = Field(default=None, primary_key=True)
    subject: str
    body: str
    sent_at: datetime
    sender_id: int = Field(foreign_key="contacts.id", nullable=False)

    # Use the concrete symbol (not a string / not Optional)
    sender: Contact = Relationship(back_populates="sent_emails")

    attachments: list["Attachment"] = Relationship(
        back_populates="email",
        sa_relationship_kwargs={"cascade": "all, delete-orphan", "single_parent": True},
    )
    recipients: list["EmailReception"] = Relationship(
        back_populates="email",
        sa_relationship_kwargs={"cascade": "all, delete-orphan", "single_parent": True},
    )
