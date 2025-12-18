"""Chat session model for storing conversation sessions linked to users and threads."""

from datetime import datetime
from typing import TYPE_CHECKING

from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from .chat_message import ChatMessage
    from .user import User


class ChatSession(SQLModel, table=True):
    """Model representing a chat session for a user on a specific thread."""

    __tablename__ = "chat_sessions"

    id: int | None = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id", nullable=False)
    thread_id: int  # Thread ID is implicit context; no separate join table needed
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

    # Relationships
    user: "User" = Relationship(back_populates="chat_sessions")
    messages: list["ChatMessage"] = Relationship(
        back_populates="session",
        sa_relationship_kwargs={"cascade": "all, delete-orphan", "single_parent": True},
    )
