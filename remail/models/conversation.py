"""Conversation model for grouping contacts."""

from typing import TYPE_CHECKING

import sqlalchemy
from sqlmodel import Field, Relationship, SQLModel

from remail.enums import ConversationType

# Import at runtime for SQLAlchemy
from .conversation_contact import ConversationContact  # noqa: F401
from .thread import Thread
from .user_conversation import UserConversation  # noqa: F401

if TYPE_CHECKING:
    from .contact import Contact
    from .thread import Thread
    from .user import User


class Conversation(SQLModel, table=True):
    """Conversation model representing a group of contacts."""

    __tablename__ = "conversations"

    id: int | None = Field(default=None, primary_key=True)
    custom_name: str | None = None
    is_favorite: bool = Field(default=False, nullable=False)
    conversation_type: ConversationType = Field(nullable=False, default=ConversationType.GROUP)
    type: ConversationType = Field(
        default=ConversationType.CONVERSATION,
        sa_column=sqlalchemy.Column(sqlalchemy.Enum(ConversationType), nullable=True),
    )

    # Many-to-many relationship with contacts (participants in the conversation)
    contacts: list["Contact"] = Relationship(
        back_populates="conversations",
        link_model=ConversationContact,
    )
    # Many-to-many relationship with users (users who can see this conversation)
    users: list["User"] = Relationship(
        back_populates="conversations",
        link_model=UserConversation,
    )
    # one-to-many
    threads: list["Thread"] = Relationship(
        back_populates="conversation",
    )
