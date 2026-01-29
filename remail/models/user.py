from datetime import datetime
from typing import TYPE_CHECKING

import sqlalchemy
from sqlmodel import Field, Relationship, SQLModel

from remail.enums import Protocol

# Import at runtime for SQLAlchemy
from .user_conversation import UserConversation  # noqa: F401

if TYPE_CHECKING:
    from .chat_session import ChatSession
    from .conversation import Conversation


class User(SQLModel, table=True):
    __tablename__ = "users"

    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(default="John Doe")  # Real name (e.g. John Smith)
    host: str = Field(default="--unspecified-host--")  # hostname
    username: str = Field(default="--unspecified-username--")  # imap / smtp username
    email: str = Field(  # public email address (not always the same as username!!!!)
        sa_column=sqlalchemy.Column(sqlalchemy.String, unique=True, index=True, nullable=False)
    )
    password: str = Field(default="--unspecified-password--")  # imap / smtp password
    protocol: Protocol = Field(
        sa_column=sqlalchemy.Column(sqlalchemy.Enum(Protocol), nullable=False)
    )
    last_refresh: datetime = Field(default=datetime.min)

    # Many-to-many relationship with conversations
    conversations: list["Conversation"] = Relationship(
        back_populates="users",
        link_model=UserConversation,
    )

    chat_sessions: list["ChatSession"] = Relationship(back_populates="user")
