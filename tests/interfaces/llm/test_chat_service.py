"""Tests for ChatService."""

from datetime import datetime

import pytest
from sqlmodel import Session

from remail.enums import ConversationType, Protocol
from remail.interfaces.llm.chat_service import ChatService
from remail.interfaces.llm.enums.llm_message_role import LLMMessageRole
from remail.models import ChatSession, Contact, Conversation, Email, Thread, User


def _create_user(session: Session, email: str) -> User:
    user = User(
        name=email.split("@")[0],
        username=email,
        email=email,
        host="imap.example.com",
        password="hash123",
        protocol=Protocol.IMAP,
    )
    session.add(user)
    session.flush()
    return user


def _create_conversation(session: Session) -> Conversation:
    conversation = Conversation(custom_name="Test Conversation", type=ConversationType.CONVERSATION)
    session.add(conversation)
    session.flush()
    return conversation


def _create_thread(session: Session, conversation_id: int) -> Thread:
    thread = Thread(title="Test Thread", conversation_id=conversation_id)
    session.add(thread)
    session.flush()
    return thread


def _create_contact(session: Session, email: str, name: str) -> Contact:
    contact = Contact(
        name=name,
        email_address=email,
        first_name=name.split()[0],
        last_name="",
        is_known=True,
    )
    session.add(contact)
    session.flush()
    return contact


class TestChatService:
    """Test suite for ChatService."""

    @pytest.fixture
    def service(self, test_engine):
        svc = ChatService()
        svc.engine = test_engine
        return svc

    @pytest.fixture
    def user_thread(self, test_engine):
        with Session(test_engine) as session:
            user = _create_user(session, "test@example.com")
            conversation = _create_conversation(session)
            thread = _create_thread(session, conversation.id)
            session.commit()
            return user.id, thread.id

    def test_get_or_create_session_returns_existing(
        self, service: ChatService, user_thread: tuple[int, int]
    ):
        user_id, thread_id = user_thread
        session1 = service.get_or_create_session(user_id, thread_id)
        session2 = service.get_or_create_session(user_id, thread_id)
        assert isinstance(session1, ChatSession)
        assert session1.id == session2.id

    def test_save_message_and_get_session_messages(
        self, service: ChatService, user_thread: tuple[int, int]
    ):
        user_id, thread_id = user_thread
        chat_session = service.get_or_create_session(user_id, thread_id)
        assert chat_session.id is not None

        session_id = chat_session.id
        service.save_message(session_id, LLMMessageRole.USER, "Hello")
        service.save_message(session_id, LLMMessageRole.ASSISTANT, "Hi there")

        messages = service.get_session_messages(session_id)
        assert len(messages) == 2
        assert messages[0].role == LLMMessageRole.USER
        assert messages[0].content == "Hello"
        assert messages[1].role == LLMMessageRole.ASSISTANT
        assert messages[1].content == "Hi there"

    def test_build_thread_context_formats_messages(self, service: ChatService, test_engine):
        with Session(test_engine) as session:
            conversation = _create_conversation(session)
            thread = _create_thread(session, conversation.id)
            thread_id = thread.id
            contact = _create_contact(session, "alice@example.com", "Alice")

            email1 = Email(
                body="First message",
                sent_at=datetime(2025, 1, 1, 12, 0, 0),
                sender_id=contact.id,
                thread_id=thread.id,
            )
            email2 = Email(
                body="Second message",
                sent_at=datetime(2025, 1, 2, 12, 0, 0),
                sender_id=contact.id,
                thread_id=thread.id,
            )
            session.add_all([email1, email2])
            session.commit()

        context = service.build_thread_context(thread_id)
        assert "Thread title: Test Thread" in context
        assert "Messages:" in context
        assert "First message" in context
        assert "Second message" in context
        assert context.index("First message") < context.index("Second message")
