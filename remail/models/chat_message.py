from datetime import datetime
from typing import TYPE_CHECKING

import sqlalchemy
from sqlmodel import Field, Relationship, SQLModel

from remail.interfaces.llm.enums.llm_message_role import LLMMessageRole

if TYPE_CHECKING:
    from .chat_session import ChatSession


class ChatMessage(SQLModel, table=True):
    __tablename__ = "chat_messages"

    id: int | None = Field(default=None, primary_key=True)
    session_id: int = Field(foreign_key="chat_sessions.id")
    role: LLMMessageRole = Field(
        sa_column=sqlalchemy.Column(sqlalchemy.Enum(LLMMessageRole), nullable=False)
    )
    content: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)

    session: "ChatSession" = Relationship(back_populates="messages")
