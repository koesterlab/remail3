from datetime import datetime
from enum import Enum, auto

import sqlalchemy
from sqlmodel import Field, Relationship, SQLModel


def id_field(table_name: str):
    sequence = sqlalchemy.Sequence(f"{table_name}_id_seq")
    return Field(
        default=None,
        primary_key=True,
        sa_column_args=[sequence],
        sa_column_kwargs={"server_default": sequence.next_value()},
    )


class Contact(SQLModel, table=True):
    id: int | None = id_field("contact")
    email_address: str
    name: str | None = None
    receptions: list["EmailReception"] = Relationship(back_populates="contact")
    sent_emails: list["Email"] = Relationship(back_populates="sender")


class RecipientKind(Enum):
    to = "to"
    cc = "cc"
    bcc = "bcc"


class EmailReception(SQLModel, table=True):
    email_id: int = Field(foreign_key="email.id", primary_key=True)
    contact_id: int = Field(foreign_key="contact.id", primary_key=True)
    kind: RecipientKind
    email: "Email" = Relationship(back_populates="recipients")
    contact: "Contact" = Relationship(back_populates="receptions")


class Attachment(SQLModel, table=True):
    id: int | None = id_field("attachment")
    filename: str
    email_id: int = Field(default=None, foreign_key="email.id")
    email: "Email" = Relationship(back_populates="attachments")


class Email(SQLModel, table=True):
    id: int | None = id_field("email")
    message_id: str
    sender_id: int = Field(foreign_key="contact.id")
    sender: "Contact" = Relationship(back_populates="sent_emails")
    subject: str
    body: str
    attachments: list[Attachment] | None = Relationship(back_populates="email")
    recipients: list[EmailReception] = Relationship(back_populates="email")
    date: datetime
    urgency: int | None


class Protocol(Enum):
    IMAP = auto()
    EXCHANGE = auto()


class User(SQLModel, table=True):
    id: int | None = id_field("user")
    name: str
    email: str
    protocol: Protocol = Field(sa_column=sqlalchemy.Column(sqlalchemy.Enum(Protocol)))
    extra_information: str
    """if Exchange: extra_information = username else: extra_information = host"""
    last_refresh: datetime | None = None
