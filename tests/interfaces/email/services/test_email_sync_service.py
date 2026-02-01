"""Tests for EmailSyncService."""

from datetime import datetime
from email.message import EmailMessage
from unittest.mock import MagicMock

import pytest
from sqlmodel import Session

from remail.enums import Protocol
from remail.interfaces.email.services.email_sync_service import EmailSyncService
from remail.models import Contact, Email, Thread, User


@pytest.fixture
def mock_protocol():
    """Create a mock IMAP protocol."""
    protocol = MagicMock()
    protocol.logged_in = True
    protocol.fetch_emails.return_value = []
    return protocol


@pytest.fixture
def mock_email_parser():
    """Create a mock email parser."""
    return MagicMock()


def create_test_user(engine) -> User:
    """Helper to create the test user in the database."""
    with Session(engine) as session:
        user = User(
            name="test",
            username="test@example.com",
            email="test@example.com",
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

    def test_sync_emails_no_new_emails(self, mock_protocol, mock_email_parser, test_engine):
        """Test sync when there are no new emails."""
        user = create_test_user(test_engine)
        service = EmailSyncService(
            protocol=mock_protocol, email_parser=mock_email_parser, user_id=user.id
        )
        mock_protocol.fetch_emails.return_value = []

        before_sync = datetime.now()
        result = service.sync_emails()

        assert result["status"] == "success"
        assert result["synced_count"] == 0

        with Session(test_engine) as session:
            from sqlmodel import select

            refreshed = session.exec(select(User).where(User.id == user.id)).first()
            assert refreshed is not None
            assert refreshed.last_refresh >= before_sync

    def test_sync_emails_fails_if_user_not_found(self, mock_protocol, mock_email_parser):
        """Test that sync fails if user does not exist."""
        service = EmailSyncService(
            protocol=mock_protocol, email_parser=mock_email_parser, user_id=999
        )

        result = service.sync_emails()

        assert result["status"] == "error"
        assert "not found" in result["message"].lower()
        assert result["synced_count"] == 0

    def test_sync_emails_calls_parser_for_each_email(
        self, mock_protocol, mock_email_parser, test_engine
    ):
        """Test that sync calls the parser for each email."""
        user = create_test_user(test_engine)
        service = EmailSyncService(
            protocol=mock_protocol, email_parser=mock_email_parser, user_id=user.id
        )

        msg1 = EmailMessage()
        msg1["Message-ID"] = "<msg-1@example.com>"
        msg2 = EmailMessage()
        msg2["Message-ID"] = "<msg-2@example.com>"

        mock_protocol.fetch_emails.return_value = [(1, msg1), (2, msg2)]

        result = service.sync_emails()

        assert result["status"] == "success"
        assert mock_email_parser.process_email.call_count == 2

        called_uids = [call.args[2] for call in mock_email_parser.process_email.call_args_list]
        assert called_uids == [1, 2]

        for call in mock_email_parser.process_email.call_args_list:
            assert isinstance(call.args[1], User)

    def test_sync_emails_skips_duplicate_message_id(
        self, mock_protocol, mock_email_parser, test_engine
    ):
        """Test that sync skips emails with duplicate message_id."""
        user = create_test_user(test_engine)
        service = EmailSyncService(
            protocol=mock_protocol, email_parser=mock_email_parser, user_id=user.id
        )

        with Session(test_engine) as session:
            sender = Contact(name="Sender", email_address="sender@example.com")
            from remail.models import Conversation

            conversation = Conversation(custom_name="C")
            session.add_all([conversation, sender])
            session.commit()

            thread = Thread(title="T", conversation_id=conversation.id)
            session.add(thread)
            session.commit()
            session.refresh(sender)
            session.refresh(thread)

            existing = Email(
                message_id="<dup@example.com>",
                body="Body",
                sent_at=datetime.now(),
                sender_id=sender.id,
                thread_id=thread.id,
            )
            session.add(existing)
            session.commit()

        dup_msg = EmailMessage()
        dup_msg["Message-ID"] = "<dup@example.com>"

        mock_protocol.fetch_emails.return_value = [(42, dup_msg)]

        result = service.sync_emails()

        assert result["status"] == "success"
        assert result["synced_count"] == 0
        assert result["skipped_count"] == 1
        mock_email_parser.process_email.assert_not_called()

    def test_sync_emails_handles_fetch_error(self, mock_protocol, mock_email_parser, test_engine):
        """Test that sync handles IMAP fetch errors gracefully."""
        user = create_test_user(test_engine)
        service = EmailSyncService(
            protocol=mock_protocol, email_parser=mock_email_parser, user_id=user.id
        )
        mock_protocol.fetch_emails.side_effect = Exception("Connection failed")

        result = service.sync_emails()

        assert result["status"] == "error"
        assert "Connection failed" in result["message"]

    def test_sync_emails_logs_in_when_needed(self, mock_protocol, mock_email_parser, test_engine):
        """Test that sync triggers login when protocol is not logged in."""
        user = create_test_user(test_engine)
        service = EmailSyncService(
            protocol=mock_protocol, email_parser=mock_email_parser, user_id=user.id
        )
        mock_protocol.logged_in = False
        mock_protocol.fetch_emails.return_value = []

        service.sync_emails()

        mock_protocol.login.assert_called_once()
