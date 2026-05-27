"""Join table for User and Conversation with favorite preference."""

from sqlmodel import Field, SQLModel


class UserConversation(SQLModel, table=True):
    """Links users to conversations with favorite preferences."""

    __tablename__ = "user_conversations"

    user_id: int = Field(foreign_key="users.id", primary_key=True)
    conversation_id: int = Field(foreign_key="conversations.id", primary_key=True)
