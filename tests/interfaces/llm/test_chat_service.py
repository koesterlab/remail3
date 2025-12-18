"""Tests for ChatService."""

from datetime import UTC, datetime

import pytest
from sqlmodel import Session, select

from remail.interfaces.llm.services.chat_service import ChatService
from remail.models import ChatMessage, ChatSession, Contact, Email, User


@pytest.fixture
def user(session: Session) -> User:
    """Create a test user."""
    user = User(
        name="Test User",
        email="test@example.com",
        password="hashedpassword123",
        protocol="IMAP",
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


@pytest.fixture
def contact(session: Session) -> Contact:
    """Create a test contact."""
    contact = Contact(name="Sender", email_address="sender@example.com")
    session.add(contact)
    session.commit()
    session.refresh(contact)
    return contact


@pytest.fixture
def email(session: Session, contact: Contact) -> Email:
    """Create a test email."""
    email = Email(
        subject="Test Email",
        body="This is a test email body with important information.",
        sent_at=datetime.now(UTC),
        sender_id=contact.id,
    )
    session.add(email)
    session.commit()
    session.refresh(email)
    return email


@pytest.fixture
def chat_service(session: Session) -> ChatService:
    """Create a ChatService instance."""
    return ChatService(session)


class TestChatService:
    """Test suite for ChatService."""

    def test_get_or_create_session_new(self, chat_service: ChatService, user: User, session: Session):
        """Test creating a new chat session."""
        result = chat_service.get_or_create_session(user.id, thread_id=123)

        assert result.id is not None
        assert result.user_id == user.id
        assert result.thread_id == 123
        assert result.created_at is not None
        assert result.updated_at is not None

    def test_get_or_create_session_existing(
        self, chat_service: ChatService, user: User, session: Session
    ):
        """Test retrieving an existing chat session."""
        # Create first session
        session1 = chat_service.get_or_create_session(user.id, thread_id=123)
        session1_id = session1.id

        # Get same session again
        session2 = chat_service.get_or_create_session(user.id, thread_id=123)

        assert session2.id == session1_id
        # Should not create a new one

    def test_get_or_create_session_different_threads(
        self, chat_service: ChatService, user: User, session: Session
    ):
        """Test creating sessions for different threads."""
        session1 = chat_service.get_or_create_session(user.id, thread_id=123)
        session2 = chat_service.get_or_create_session(user.id, thread_id=456)

        assert session1.id != session2.id
        assert session1.thread_id == 123
        assert session2.thread_id == 456

    def test_save_message(self, chat_service: ChatService, user: User, session: Session):
        """Test saving a message."""
        chat_session = chat_service.get_or_create_session(user.id, thread_id=123)

        message = chat_service.save_message(chat_session.id, "user", "Hello, assistant!")

        assert message.id is not None
        assert message.session_id == chat_session.id
        assert message.role == "user"
        assert message.content == "Hello, assistant!"
        assert message.created_at is not None

    def test_save_multiple_messages(
        self, chat_service: ChatService, user: User, session: Session
    ):
        """Test saving multiple messages."""
        chat_session = chat_service.get_or_create_session(user.id, thread_id=123)

        msg1 = chat_service.save_message(chat_session.id, "user", "First message")
        msg2 = chat_service.save_message(chat_session.id, "assistant", "First response")
        msg3 = chat_service.save_message(chat_session.id, "user", "Second message")

        assert msg1.id != msg2.id != msg3.id
        assert msg1.role == "user"
        assert msg2.role == "assistant"
        assert msg3.role == "user"

    def test_get_session_messages_empty(
        self, chat_service: ChatService, user: User, session: Session
    ):
        """Test retrieving messages from an empty session."""
        chat_session = chat_service.get_or_create_session(user.id, thread_id=123)

        messages = chat_service.get_session_messages(chat_session.id)

        assert len(messages) == 0

    def test_get_session_messages_ordered(
        self, chat_service: ChatService, user: User, session: Session
    ):
        """Test that messages are ordered by creation time."""
        chat_session = chat_service.get_or_create_session(user.id, thread_id=123)

        msg1 = chat_service.save_message(chat_session.id, "user", "First")
        msg2 = chat_service.save_message(chat_session.id, "assistant", "Second")
        msg3 = chat_service.save_message(chat_session.id, "user", "Third")

        messages = chat_service.get_session_messages(chat_session.id)

        assert len(messages) == 3
        assert messages[0].content == "First"
        assert messages[1].content == "Second"
        assert messages[2].content == "Third"

    def test_build_thread_context_empty(self, chat_service: ChatService, session: Session):
        """Test building context for non-existent thread."""
        context = chat_service.build_thread_context(thread_id=999)

        assert context == ""

    def test_build_thread_context_single_email(
        self, chat_service: ChatService, email: Email, session: Session
    ):
        """Test building context from a single email."""
        context = chat_service.build_thread_context(thread_id=email.id)

        assert "Thread context:" in context
        assert email.subject in context
        assert email.body in context
        assert email.sender.name in context
        assert email.sender.email_address in context

    def test_build_thread_context_format(
        self, chat_service: ChatService, email: Email, session: Session
    ):
        """Test the format of built thread context."""
        context = chat_service.build_thread_context(thread_id=email.id)

        assert "From:" in context
        assert "Subject:" in context
        assert "Date:" in context

    def test_update_session_timestamp(
        self, chat_service: ChatService, user: User, session: Session
    ):
        """Test updating session timestamp."""
        chat_session = chat_service.get_or_create_session(user.id, thread_id=123)
        original_timestamp = chat_session.updated_at

        # Wait a moment and update
        import time
        time.sleep(0.01)

        chat_service.update_session_timestamp(chat_session.id)

        # Refresh to get updated value
        statement = select(ChatSession).where(ChatSession.id == chat_session.id)
        updated_session = session.exec(statement).first()

        assert updated_session.updated_at > original_timestamp

    def test_chat_flow_persistence(
        self, chat_service: ChatService, user: User, session: Session
    ):
        """Test a complete chat flow with message persistence."""
        # Create session
        chat_session = chat_service.get_or_create_session(user.id, thread_id=123)

        # Exchange messages
        chat_service.save_message(chat_session.id, "user", "What is machine learning?")
        chat_service.save_message(
            chat_session.id, "assistant", "Machine learning is a subset of AI..."
        )
        chat_service.save_message(chat_session.id, "user", "Tell me more about neural networks.")
        chat_service.save_message(chat_session.id, "assistant", "Neural networks are...")

        # Retrieve all messages
        messages = chat_service.get_session_messages(chat_session.id)

        assert len(messages) == 4
        assert messages[0].role == "user"
        assert messages[1].role == "assistant"
        assert messages[2].role == "user"
        assert messages[3].role == "assistant"

    def test_multiple_sessions_isolated(
        self, chat_service: ChatService, user: User, session: Session
    ):
        """Test that messages from different sessions are isolated."""
        session1 = chat_service.get_or_create_session(user.id, thread_id=1)
        session2 = chat_service.get_or_create_session(user.id, thread_id=2)

        chat_service.save_message(session1.id, "user", "Message in session 1")
        chat_service.save_message(session2.id, "user", "Message in session 2")

        messages1 = chat_service.get_session_messages(session1.id)
        messages2 = chat_service.get_session_messages(session2.id)

        assert len(messages1) == 1
        assert len(messages2) == 1
        assert messages1[0].content == "Message in session 1"
        assert messages2[0].content == "Message in session 2"
