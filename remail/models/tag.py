"""Tag model for manual and automatic email classification."""

from typing import TYPE_CHECKING

from sqlalchemy import Column, String
from sqlmodel import Field, Relationship, SQLModel

from .tag_email import EmailTag

if TYPE_CHECKING:
    from .email import Email


class Tag(SQLModel, table=True):
    """Reusable tag definition that can be attached to many emails."""

    __tablename__ = "tags"

    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(sa_column=Column(String, unique=True, nullable=False, index=True))
    description: str | None = Field(default=None)

    emails: list["Email"] = Relationship(
        back_populates="tags",
        link_model=EmailTag,
    )
