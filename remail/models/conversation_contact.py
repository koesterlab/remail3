"""Join table for Conversation and Contact."""

from sqlmodel import Field, SQLModel


class ConversationContact(SQLModel, table=True):
    """Links conversations with their contacts (participants)."""

    __tablename__ = "conversation_contacts"

    conversation_id: int = Field(foreign_key="conversations.id", primary_key=True)
    contact_id: int = Field(foreign_key="contacts.id", primary_key=True)
