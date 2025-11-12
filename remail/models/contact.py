from typing import TYPE_CHECKING

from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from .email import Email
    from .email_reception import EmailReception


class Contact(SQLModel, table=True):
    __tablename__ = "contacts"

    id: int | None = Field(default=None, primary_key=True)
    name: str
    email_address: str

    receptions: list["EmailReception"] = Relationship(back_populates="contact")
    sent_emails: list["Email"] = Relationship(back_populates="sender")
