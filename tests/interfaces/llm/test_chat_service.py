"""Tests for ChatService."""

from datetime import datetime
from unittest.mock import patch

import pytest
from sqlalchemy.pool import StaticPool
from sqlmodel import Session, SQLModel, create_engine, select

from remail.enums.contact_type import ContactType
from remail.enums.protocol import Protocol
from remail.interfaces.llm.chat_service import ChatService
from remail.interfaces.llm.enums.llm_message_role import LLMMessageRole
from remail.models import ChatSession, Contact, Email, Thread, User


@pytest.fixture
def test_engine():
    """Create a test database engine."""
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        echo=False,
    )
    SQLModel.metadata.create_all(engine)
    yield engine
    SQLModel.metadata.drop_all(engine)


@pytest.fixture
def service(test_engine):
    """Create a ChatService instance with test engine."""
    with patch("remail.interfaces.llm.chat_service.engine", test_engine):
        svc = ChatService()
        svc.engine = test_engine
        return svc


@pytest.fixture
def user_thread_data(test_engine):
    """Seed a user, thread, and email for context tests."""
    with Session(test_engine) as session:
        user = User(
            name="test-user",
            email="test@example.com",
            host="imap.example.com",
            password="hash123",
            protocol=Protocol.IMAP,
        )
        contact = Contact(
            name="Sender",
            email_address="sender@example.com",
            first_name="Sender",
            last_name="One",
            contact_type=ContactType.PRIVATE,
        )
        thread = Thread(title="Support Thread")

        session.add_all([user, contact, thread])
        session.flush()

        email = Email(
            subject="Test subject",
            body="Hello from the thread",
            sent_at=datetime(2024, 5, 30, 10, 0, 0),
            sender_id=contact.id,
            thread_id=thread.id,
        )
        session.add(email)
        session.commit()

        return user.id, thread.id


class TestChatService:
    """Test suite for ChatService."""

    def test_get_or_create_session_reuses_existing(
        self, service: ChatService, test_engine, user_thread_data
    ):
        """Test that get_or_create_session reuses existing sessions."""
        user_id, thread_id = user_thread_data

        session_one = service.get_or_create_session(user_id, thread_id)
        session_two = service.get_or_create_session(user_id, thread_id)

        assert session_one.id == session_two.id

        with Session(test_engine) as session:
            count = session.exec(
                select(ChatSession).where(
                    ChatSession.user_id == user_id,
                    ChatSession.thread_id == thread_id,
                )
            ).all()

        assert len(count) == 1

    def test_save_and_get_session_messages(self, service: ChatService, user_thread_data):
        """Test saving and retrieving messages in order."""
        user_id, thread_id = user_thread_data
        chat_session = service.get_or_create_session(user_id, thread_id)

        service.save_message(chat_session.id, LLMMessageRole.USER, "Hello")
        service.save_message(chat_session.id, LLMMessageRole.ASSISTANT, "Hi there")

        messages = service.get_session_messages(chat_session.id)

        assert [msg.role for msg in messages] == [
            LLMMessageRole.USER,
            LLMMessageRole.ASSISTANT,
        ]
        assert messages[0].content == "Hello"
        assert messages[1].content == "Hi there"

    def test_build_thread_context_includes_email_data(self, service: ChatService, user_thread_data):
        """Test that thread context includes email metadata and body."""
        _, thread_id = user_thread_data

        context = service.build_thread_context(thread_id)

        assert "Thread title: Support Thread" in context
        assert "Subject: Test subject" in context
        assert "Hello from the thread" in context
        assert "sender@example.com" in context

    def test_clear_session_messages(self, service: ChatService, user_thread_data):
        """Test clearing all session messages."""
        user_id, thread_id = user_thread_data
        chat_session = service.get_or_create_session(user_id, thread_id)

        service.save_message(chat_session.id, LLMMessageRole.USER, "Hello")
        service.clear_session_messages(chat_session.id)

        messages = service.get_session_messages(chat_session.id)

        assert messages == []
