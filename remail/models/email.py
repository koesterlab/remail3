from datetime import datetime
from typing import TYPE_CHECKING

from sqlmodel import Field, Relationship, SQLModel

# Make target symbol available at runtime so SA can resolve it
from .contact import Contact  # noqa: F401
from .thread import Thread

if TYPE_CHECKING:
    from .attachment import Attachment
    from .email_reception import EmailReception
    from .email_tag import EmailTag


class Email(SQLModel, table=True):
    __tablename__ = "emails"

    id: int | None = Field(default=None, primary_key=True)
    imap_uid: int | None = Field(default=None)
    message_id: str | None = Field(default=None, unique=True, index=True)
    body: str
    sent_at: datetime
    due_date: datetime | None = Field(default=None)
    sender_id: int = Field(foreign_key="contacts.id", nullable=False)
    thread_id: int = Field(foreign_key="threads.id", nullable=True)
    deleted: bool = Field(default=False, nullable=False)
    read: bool = Field(default=False, nullable=False)

    sender: Contact = Relationship(back_populates="sent_emails")
    thread: Thread = Relationship(back_populates="messages")

    attachments: list["Attachment"] = Relationship(
        back_populates="email",
        sa_relationship_kwargs={"cascade": "all, delete-orphan", "single_parent": True},
        cascade_delete=True,
    )
    recipients: list["EmailReception"] = Relationship(
        back_populates="email",
        cascade_delete=True,
        sa_relationship_kwargs={"cascade": "all, delete-orphan", "single_parent": True},
    )
    tags: list["EmailTag"] = Relationship(
        back_populates="email",
        cascade_delete=True,
        sa_relationship_kwargs={"cascade": "all, delete-orphan", "single_parent": True},
    )
