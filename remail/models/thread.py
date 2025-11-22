from typing import TYPE_CHECKING

from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from .email import Email


class Thread(SQLModel, table=True):
    __tablename__ = "threads"

    id: int | None = Field(default=None, primary_key=True)
    messages: list["Email"] = Relationship(back_populates="thread")
