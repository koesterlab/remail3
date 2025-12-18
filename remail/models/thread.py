from typing import TYPE_CHECKING, Optional

from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from .conversation import Conversation
    from .email import Email


class Thread(SQLModel, table=True):
    __tablename__ = "threads"

    id: int | None = Field(default=None, primary_key=True)
    title: str = Field(default="")
    conversation_id: int | None = Field(default=None, foreign_key="conversations.id")

    messages: list["Email"] = Relationship(back_populates="thread")
    conversation: Optional["Conversation"] = Relationship(back_populates="thread")
