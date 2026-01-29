from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import UniqueConstraint
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from .chat_message import ChatMessage
    from .thread import Thread
    from .user import User


class ChatSession(SQLModel, table=True):
    __tablename__ = "chat_sessions"
    __table_args__ = (UniqueConstraint("user_id", "thread_id"),)

    id: int | None = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id")
    thread_id: int = Field(foreign_key="threads.id")
    created_at: datetime = Field(default_factory=datetime.utcnow)

    user: "User" = Relationship(back_populates="chat_sessions")
    thread: "Thread" = Relationship(back_populates="chat_sessions")
    messages: list["ChatMessage"] = Relationship(
        back_populates="session",
        sa_relationship_kwargs={"cascade": "all, delete-orphan", "single_parent": True},
    )
