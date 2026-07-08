from typing import TYPE_CHECKING

from sqlmodel import Field, Relationship, SQLModel

from .email_tag import EmailTag  # noqa: F401 - needed at runtime for link_model

if TYPE_CHECKING:
    from .email import Email


class Tag(SQLModel, table=True):
    __tablename__ = "tags"

    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(index=True, unique=True)
    description: str = Field(default="")

    emails: list["Email"] = Relationship(back_populates="tags", link_model=EmailTag)
