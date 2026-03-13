"""Conversation model for grouping contacts."""

from typing import TYPE_CHECKING

import sqlalchemy
from sqlmodel import Field, Relationship, SQLModel

from remail.enums import ConversationType

# Import at runtime for SQLAlchemy
from .conversation_contact import ConversationContact  # noqa: F401
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
    user_id:int | None = Field(default=None, foreign_key="users.id")
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
    # Many-to-one relationship with users (user who can see this conversation)
    user: "User" = Relationship(back_populates="conversations")
    # one-to-many
    threads: list["Thread"] = Relationship(
        back_populates="conversation",
        cascade_delete=True,
    )
