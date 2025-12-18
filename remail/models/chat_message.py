"""Chat message model for storing individual messages in a chat session."""

from datetime import datetime
from typing import TYPE_CHECKING

from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from .chat_session import ChatSession


class ChatMessage(SQLModel, table=True):
    """Model representing a single message in a chat session."""

    __tablename__ = "chat_messages"

    id: int | None = Field(default=None, primary_key=True)
    session_id: int = Field(foreign_key="chat_sessions.id", nullable=False)
    role: str  # "user" or "assistant"
    content: str
    created_at: datetime = Field(default_factory=datetime.now)

    # Relationships
    session: "ChatSession" = Relationship(back_populates="messages")
