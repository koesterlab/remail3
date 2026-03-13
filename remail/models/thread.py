from datetime import datetime
from typing import TYPE_CHECKING

from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from .conversation import Conversation
    from .email import Email


class Thread(SQLModel, table=True):
    __tablename__ = "threads"

    id: int | None = Field(default=None, primary_key=True)
    title: str = Field(default="")
    conversation_id: int = Field(foreign_key="conversations.id")
    messages: list["Email"] = Relationship(back_populates="thread", cascade_delete=True)
    conversation: "Conversation" = Relationship(back_populates="threads")
    unread_count: int = Field(default=0)
    last_message_time: datetime | None = Field(default=None)
