"""Initialize database tables."""
from sqlmodel import SQLModel
from remail.database.db import engine

# Import all models to register them with SQLModel
from remail.models import (  # noqa: F401
    Attachment,
    Contact,
    Conversation,
    ConversationContact,
    Email,
    EmailReception,
    Settings,
    Thread,
    User,
    UserConversation,
)


def init_db():
    """Create all database tables."""
    SQLModel.metadata.create_all(engine)


if __name__ == "__main__":
    init_db()
    print("Database initialized successfully!")