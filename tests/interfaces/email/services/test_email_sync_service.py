"""Tests for EmailSyncService."""

from datetime import datetime
from unittest.mock import MagicMock

import pytest
from sqlmodel import Session

from remail.enums import Protocol
from remail.interfaces.email.services.email_sync_service import EmailSyncService
from remail.models import (
    Contact,
    Conversation,
    Email,
    Thread,
    User,
)


@pytest.fixture
def mock_protocol():
    """Create a mock IMAP protocol."""
    protocol = MagicMock()
    protocol.fetch_emails.return_value = []
    return protocol


@pytest.fixture
def mock_email_parser():
    """Create a mock email parser."""
    return MagicMock()


@pytest.fixture
def service(mock_protocol, mock_email_parser):
    """Create an EmailSyncService instance."""
    return EmailSyncService(
        protocol=mock_protocol,
        email_parser=mock_email_parser,
        username="test@example.com",
    )


def create_test_user(engine) -> User:
    """Helper to create the test user in the database."""
    with Session(engine) as session:
        user = User(
            name="test",
            username="test@example.com",
            host="imap.example.com",
            password="",
            protocol=Protocol.IMAP,
        )
        session.add(user)
        session.commit()
        session.refresh(user)
        return user


class TestEmailSyncService:
    """Test suite for EmailSyncService."""

    def test_sync_emails_no_new_emails(self, service, mock_protocol, test_engine):
        """Test sync when there are no new emails."""
        mock_protocol.fetch_emails.return_value = []
        create_test_user(test_engine)

        result = service.sync_emails()

        assert result["status"] == "success"
        assert result["synced_count"] == 0

    def test_sync_emails_fails_if_user_not_found(self, service, mock_protocol, test_engine):
        """Test that sync fails if user does not exist."""
        mock_protocol.fetch_emails.return_value = []

        with pytest.raises(ValueError, match="not found"):
            service.sync_emails()

    def test_sync_emails_creates_contact_for_sender(self, service, mock_protocol, test_engine):
        """Test that sync creates a contact for email sender."""
        # Create a mock raw email
        mock_email = MagicMock()
        mock_email.subject = "Test Subject"
        mock_email.body = "Test Body"
        mock_email.date = datetime(2024, 1, 15, 10, 0, 0)
        mock_email.sender = ("John Doe", "john@example.com")
        mock_email.recipients = []
        mock_email.attachments = []
        mock_email.message_id = "<test123@example.com>"

        mock_protocol.fetch_emails.return_value = [mock_email]
        create_test_user(test_engine)

        result = service.sync_emails()

        assert result["status"] == "success"
        assert result["synced_count"] == 1

        # Check contact was created
        with Session(test_engine) as session:
            from sqlmodel import select

            contact = session.exec(
                select(Contact).where(Contact.email_address == "john@example.com")
            ).first()
            assert contact is not None
            assert contact.name == "John Doe"
            assert contact.first_name == "John"
            assert contact.last_name == "Doe"

    def test_sync_emails_creates_thread(self, service, mock_protocol, test_engine):
        """Test that sync creates a thread for emails."""
        mock_email = MagicMock()
        mock_email.subject = "Hello World"
        mock_email.body = "Test content"
        mock_email.date = datetime(2024, 1, 15, 10, 0, 0)
        mock_email.sender = ("Sender", "sender@example.com")
        mock_email.recipients = []
        mock_email.attachments = []
        mock_email.message_id = "<test456@example.com>"

        mock_protocol.fetch_emails.return_value = [mock_email]
        create_test_user(test_engine)

        service.sync_emails()

        with Session(test_engine) as session:
            from sqlmodel import select

            thread = session.exec(select(Thread)).first()
            assert thread is not None
            assert thread.title == "Hello World"

    def test_sync_emails_creates_conversation(self, service, mock_protocol, test_engine):
        """Test that sync creates a conversation for participants."""
        mock_email = MagicMock()
        mock_email.subject = "Group Email"
        mock_email.body = "Test"
        mock_email.date = datetime(2024, 1, 15, 10, 0, 0)
        mock_email.sender = ("Alice", "alice@example.com")
        mock_email.recipients = []
        mock_email.attachments = []
        mock_email.message_id = "<conv123@example.com>"

        mock_protocol.fetch_emails.return_value = [mock_email]
        create_test_user(test_engine)

        service.sync_emails()

        with Session(test_engine) as session:
            from sqlmodel import select

            conversation = session.exec(select(Conversation)).first()
            assert conversation is not None

    def test_sync_emails_updates_last_refresh(self, service, mock_protocol, test_engine):
        """Test that sync updates user's last_refresh timestamp."""
        mock_protocol.fetch_emails.return_value = []
        create_test_user(test_engine)

        before_sync = datetime.now()
        service.sync_emails()

        with Session(test_engine) as session:
            from sqlmodel import select

            user = session.exec(select(User).where(User.username == "test@example.com")).first()
            assert user is not None
            assert user.last_refresh is not None
            assert user.last_refresh >= before_sync

    def test_sync_emails_handles_fetch_error(self, service, mock_protocol, test_engine):
        """Test that sync handles IMAP fetch errors gracefully."""
        mock_protocol.fetch_emails.side_effect = Exception("Connection failed")
        create_test_user(test_engine)

        result = service.sync_emails()

        assert result["status"] == "error"
        assert "Connection failed" in result["message"]

    def test_normalize_subject(self, service):
        """Test subject normalization removes reply/forward prefixes."""
        assert service._normalize_subject("Re: Hello") == "hello"
        assert service._normalize_subject("RE: RE: Hello") == "hello"
        assert service._normalize_subject("Fwd: Hello") == "hello"
        assert service._normalize_subject("FW: Hello") == "hello"
        assert service._normalize_subject("AW: Hello") == "hello"
        assert service._normalize_subject("[TAG] Hello") == "hello"
        assert service._normalize_subject("") == ""

    def test_parse_name(self, service):
        """Test name parsing into first and last name."""
        assert service._parse_name("John Doe") == ("John", "Doe")
        assert service._parse_name("John") == ("John", "")
        assert service._parse_name("John Michael Doe") == ("John", "Michael Doe")
        assert service._parse_name("") == ("", "")
        assert service._parse_name("  ") == ("", "")

    def test_extract_sender_tuple(self, service):
        """Test sender extraction from tuple format."""
        mock_email = MagicMock()
        mock_email.sender = ("John Doe", "john@example.com")

        result = service._extract_sender(mock_email)
        assert result == {"name": "John Doe", "email": "john@example.com"}

    def test_extract_sender_string(self, service):
        """Test sender extraction from string format."""
        mock_email = MagicMock()
        mock_email.sender = "john@example.com"

        result = service._extract_sender(mock_email)
        assert result == {"name": "", "email": "john@example.com"}

    def test_extract_sender_none(self, service):
        """Test sender extraction when sender is None."""
        mock_email = MagicMock()
        mock_email.sender = None

        result = service._extract_sender(mock_email)
        assert result["email"] == "unknown@unknown.com"


class TestEmailSyncServiceThreading:
    """Tests for thread organization in EmailSyncService."""

    def test_emails_grouped_into_same_thread_by_subject(self, service, mock_protocol, test_engine):
        """Test that emails with same normalized subject go into same thread."""
        # First email
        mock_email1 = MagicMock()
        mock_email1.subject = "Hello World"
        mock_email1.body = "First message"
        mock_email1.date = datetime(2024, 1, 15, 10, 0, 0)
        mock_email1.sender = ("Alice", "alice@example.com")
        mock_email1.recipients = []
        mock_email1.attachments = []
        mock_email1.message_id = "<msg1@example.com>"

        # Reply email
        mock_email2 = MagicMock()
        mock_email2.subject = "Re: Hello World"
        mock_email2.body = "Reply message"
        mock_email2.date = datetime(2024, 1, 15, 11, 0, 0)
        mock_email2.sender = ("Alice", "alice@example.com")
        mock_email2.recipients = []
        mock_email2.attachments = []
        mock_email2.message_id = "<msg2@example.com>"

        mock_protocol.fetch_emails.return_value = [mock_email1, mock_email2]
        create_test_user(test_engine)

        result = service.sync_emails()

        assert result["synced_count"] == 2

        with Session(test_engine) as session:
            from sqlmodel import select

            threads = session.exec(select(Thread)).all()
            # Both emails should be in the same thread
            assert len(threads) == 1

            emails = session.exec(select(Email)).all()
            assert len(emails) == 2
            # Both emails have same thread_id
            assert emails[0].thread_id == emails[1].thread_id
