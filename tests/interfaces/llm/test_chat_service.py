"""Tests for ChatService."""

from datetime import datetime, timedelta
from unittest.mock import patch

import pytest
from sqlalchemy.pool import StaticPool
from sqlmodel import Session, SQLModel, create_engine

from remail.enums.contact_type import ContactType
from remail.enums.protocol import Protocol
from remail.interfaces.llm.chat_service import ChatService
from remail.interfaces.llm.enums.llm_message_role import LLMMessageRole
from remail.models import ChatSession, Contact, Email, Thread, User


class TestChatService:
    """Test suite for ChatService."""

    @pytest.fixture
    def test_engine(self):
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
    def service(self, test_engine):
        """Create a ChatService instance with test engine."""
        with patch("remail.interfaces.llm.chat_service.engine", test_engine):
            svc = ChatService()
            svc.engine = test_engine
            return svc

    @pytest.fixture
    def user_and_thread(self, test_engine):
        """Create a user and thread for testing."""
        with Session(test_engine) as session:
            user = User(
                name="tester",
                email="tester@example.com",
                host="imap.example.com",
                password="hash123",
                protocol=Protocol.IMAP,
            )
            session.add(user)
            session.flush()

            thread = Thread(title="Quarterly Update")
            session.add(thread)
            session.commit()

            return user.id, thread.id

    def test_get_or_create_session_returns_existing(self, service, test_engine):
        """Ensure existing session is reused."""
        with Session(test_engine) as session:
            user = User(
                name="tester",
                email="tester2@example.com",
                host="imap.example.com",
                password="hash123",
                protocol=Protocol.IMAP,
            )
            session.add(user)
            session.flush()

            thread = Thread(title="Existing Thread")
            session.add(thread)
            session.flush()

            existing = ChatSession(user_id=user.id, thread_id=thread.id)
            session.add(existing)
            session.commit()
            session.refresh(existing)

            user_id = user.id
            thread_id = thread.id
            session_id = existing.id

        result = service.get_or_create_session(user_id=user_id, thread_id=thread_id)

        assert result.id == session_id

    def test_save_and_get_session_messages(self, service, user_and_thread):
        """Ensure messages persist and are ordered by timestamp."""
        user_id, thread_id = user_and_thread
        chat_session = service.get_or_create_session(user_id=user_id, thread_id=thread_id)

        if chat_session.id is None:
            pytest.fail("Chat session ID cannot be None")

        first_time = datetime(2024, 1, 1, 10, 0, 0)
        second_time = first_time + timedelta(seconds=10)

        service.save_message(
            session_id=chat_session.id,
            role=LLMMessageRole.USER,
            content="Hello",
            created_at=first_time,
        )
        service.save_message(
            session_id=chat_session.id,
            role=LLMMessageRole.ASSISTANT,
            content="Hi there",
            created_at=second_time,
        )

        messages = service.get_session_messages(chat_session.id)

        assert len(messages) == 2
        assert messages[0].content == "Hello"
        assert messages[0].role == LLMMessageRole.USER
        assert messages[1].content == "Hi there"
        assert messages[1].role == LLMMessageRole.ASSISTANT

    def test_build_thread_context_includes_email_data(self, service, test_engine):
        """Ensure thread context includes subject, sender, and body."""
        sent_at = datetime(2024, 1, 1, 9, 0, 0)

        with Session(test_engine) as session:
            contact = Contact(
                name="Jane Doe",
                email_address="jane@example.com",
                first_name="Jane",
                last_name="Doe",
                contact_type=ContactType.PRIVATE,
                is_known=True,
            )
            session.add(contact)
            session.flush()

            thread = Thread(title="Quarterly Update")
            session.add(thread)
            session.flush()

            email = Email(
                subject="Q4 Report",
                body="Here is the report body.",
                sent_at=sent_at,
                sender_id=contact.id,
                thread_id=thread.id,
            )
            session.add(email)
            session.commit()

            thread_id = thread.id

        context = service.build_thread_context(thread_id)

        assert "Thread \"Quarterly Update\" emails:" in context
        assert "Subject: Q4 Report" in context
        assert "Here is the report body." in context
        assert "jane@example.com" in context
