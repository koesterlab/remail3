from typing import TYPE_CHECKING

from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from .chat_message import ChatMessage


class ChatSession(SQLModel, table=True):
    __tablename__ = "chat_sessions"

    id: int | None = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id", nullable=False)
    thread_id: int = Field(foreign_key="threads.id", nullable=False)

    messages: list["ChatMessage"] = Relationship(back_populates="session")
