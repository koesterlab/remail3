from typing import TYPE_CHECKING

from models.email import Email
from models.tag_email import EmailTag
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from .tag import Tag


class Tag(SQLModel, table=True):
    __tablename__ = "tags"

    id: int | None = Field(default=None, primary_key=True)
    name: str
    description: str | None = None

    emails: list["Email"] = Relationship(
        back_populates="tags",
        link_model=EmailTag,
    )
