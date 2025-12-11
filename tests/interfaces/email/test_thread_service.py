"""Tests for ThreadService."""

from datetime import datetime
from unittest.mock import MagicMock, patch

import pytest

from remail.controllers.dtos.threads import ThreadDTO
from remail.interfaces.email.services.thread_service import ThreadService
from remail.models import Contact, Email, Thread


@pytest.fixture
def mock_session():
    """Create a mock Session."""
    with patch("remail.interfaces.email.services.thread_service.Session") as mock:
        session_instance = MagicMock()
        mock.return_value = session_instance
        yield session_instance


@pytest.fixture
def service(mock_session):
    """Create a ThreadService instance with mocked session."""
    return ThreadService()


class TestThreadService:
    """Test suite for ThreadService."""

    def test_service_initializes_with_session(self, service, mock_session):
        """Test that service initializes with Session."""
        assert service.session == mock_session

    def test_get_thread_by_id_success(self, service, mock_session):
        """Test successful thread retrieval by ID."""
        # Mock thread
        mock_thread = Thread(id=1, title="Test Thread", conversation_id=1)

        # Mock messages
        mock_contact = Contact(
            id=1,
            name="John Doe",
            email_address="john@example.com",
            first_name="John",
            last_name="Doe",
        )
        mock_email = Email(
            id=101,
            subject="Test",
            body="Hello",
            sent_at=datetime(2024, 5, 30, 10, 15, 30),
            sender_id=1,
            thread_id=1,
        )

        # Configure mock session
        def mock_get(model, id):
            if model == Thread and id == 1:
                return mock_thread
            if model == Contact and id == 1:
                return mock_contact
            return None

        mock_session.get.side_effect = mock_get

        # Mock exec for emails and attachments
        mock_exec_all = MagicMock()
        mock_exec_all.all.side_effect = [
            [mock_email],  # emails for thread
            [],  # attachments for email
        ]
        mock_session.exec.return_value = mock_exec_all

        result = service.get_thread_by_id(thread_id=1)

        assert result is not None
        assert isinstance(result, ThreadDTO)
        assert result.id == 1
        assert result.title == "Test Thread"
        assert len(result.messages) == 1

    def test_get_thread_by_id_not_found(self, service, mock_session):
        """Test thread retrieval when thread doesn't exist."""
        mock_session.get.return_value = None

        result = service.get_thread_by_id(thread_id=999)

        assert result is None
        mock_session.get.assert_called_once_with(Thread, 999)

    def test_get_thread_for_conversation(self, service, mock_session):
        """Test fetching thread for a conversation."""
        # Mock thread
        mock_thread = Thread(id=1, title="Thread 1", conversation_id=1)

        # Mock emails
        mock_email1 = Email(
            id=1,
            subject="Test 1",
            body="Body 1",
            sent_at=datetime(2024, 5, 30),
            sender_id=1,
            thread_id=1,
        )
        mock_email2 = Email(
            id=2,
            subject="Test 2",
            body="Body 2",
            sent_at=datetime(2024, 5, 31),
            sender_id=1,
            thread_id=1,
        )

        # Configure mock session
        mock_exec = MagicMock()
        mock_session.exec.return_value = mock_exec

        # First call returns thread, second call returns emails
        mock_exec.first.return_value = mock_thread
        mock_exec.all.return_value = [mock_email1, mock_email2]

        result = service.get_thread_for_conversation(conversation_id=1)

        assert result is not None
        assert result["thread_id"] == 1
        assert result["title"] == "Thread 1"
        assert result["total_count"] == 2

    def test_organize_emails_into_threads_creates_new_thread(self, service, mock_session):
        """Test organizing emails creates new thread for conversation."""
        # Create a mock thread with an ID that will be set after flush
        mock_thread = MagicMock()
        mock_thread.id = 42

        # Mock emails with different subjects
        mock_emails = [
            MagicMock(
                subject="Project Update",
                thread_id=None,
                sender_id=1,
            ),
            MagicMock(
                subject="Meeting Notes",
                thread_id=None,
                sender_id=2,
            ),
        ]

        # Mock no existing thread
        mock_session.exec.return_value.first.return_value = None

        # Track what gets added so we can simulate flush setting the ID
        def track_add(obj):
            obj.id = 42

        mock_session.add.side_effect = track_add

        service.organize_emails_into_threads(mock_emails, conversation_id=1)

        # Verify a single thread was added with all emails
        mock_session.add.assert_called_once()
        mock_session.commit.assert_called_once()

        # Both emails should be assigned to the same thread
        assert mock_emails[0].thread_id == 42
        assert mock_emails[1].thread_id == 42

    def test_build_message_dto(self, service, mock_session):
        """Test building message DTO."""
        mock_contact = Contact(
            id=1,
            name="John Doe",
            email_address="john@example.com",
            first_name="John",
            last_name="Doe",
        )
        mock_email = Email(
            id=101,
            subject="Test Subject",
            body="Test Body",
            sent_at=datetime(2024, 5, 30, 10, 15, 30),
            sender_id=1,
            thread_id=1,
        )

        mock_session.get.return_value = mock_contact
        mock_session.exec.return_value.all.return_value = []

        result = service._build_message_dto(mock_email)

        assert result.id == 101
        assert result.subject == "Test Subject"
        assert result.sender.email == "john@example.com"
        assert result.content.body == "Test Body"
        assert result.sent_at is not None
