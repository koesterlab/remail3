"""Tests for EmailSyncService."""

from unittest.mock import MagicMock, patch

import pytest
from sqlmodel import Session

from remail.enums import Protocol
from remail.interfaces.email.services.email_sync_service import EmailSyncService
from remail.models import Email, Thread, User


@pytest.fixture
def test_user(test_engine):
    """Create a test user in the database."""
    with Session(test_engine) as session:
        user = User(
            name="test",
            email="test@example.com",
            protocol=Protocol.IMAP,
            connection='{"host": "imap.example.com", "port": 993}',
        )
        session.add(user)
        session.commit()
        session.refresh(user)
        return user.id


class TestEmailSyncService:
    """Test suite for EmailSyncService."""

    def test_init_creates_protocol(self, test_engine, test_user):
        """Test that initialization creates protocol from user connection."""
        with patch("remail.interfaces.email.services.email_sync_service.ImapProtocol") as mock_imap:
            with patch("remail.interfaces.email.services.email_sync_service.EmailParser"):
                service = EmailSyncService(user_id=test_user)

                mock_imap.assert_called_once()
                assert service.user_id == test_user
                assert service.changed_conversation_ids == []
                assert service.changed_threads == []

    def test_sync_emails_no_new_emails(self, test_engine, test_user):
        """Test sync when there are no new emails."""
        with patch(
            "remail.interfaces.email.services.email_sync_service.ImapProtocol"
        ) as mock_imap_cls:
            mock_protocol = MagicMock()
            mock_protocol.fetch_emails.return_value = {}
            mock_protocol.serialize.return_value = '{"host": "imap.example.com"}'
            mock_imap_cls.return_value = mock_protocol

            with patch("remail.interfaces.email.services.email_sync_service.EmailParser"):
                service = EmailSyncService(user_id=test_user)
                service.sync_emails()

                mock_protocol.fetch_emails.assert_called_once_with(new_only=True)
                assert len(service.changed_conversation_ids) == 0

    def test_sync_emails_processes_new_emails(self, test_engine, test_user):
        """Test sync processes new emails from protocol."""
        with patch(
            "remail.interfaces.email.services.email_sync_service.ImapProtocol"
        ) as mock_imap_cls:
            mock_protocol = MagicMock()
            mock_protocol.fetch_emails.return_value = {
                1: {b"BODY[]": b"test1", b"FLAGS": []},
                2: {b"BODY[]": b"test2", b"FLAGS": []},
            }
            mock_protocol.serialize.return_value = '{"host": "imap.example.com"}'
            mock_imap_cls.return_value = mock_protocol

            with patch(
                "remail.interfaces.email.services.email_sync_service.EmailParser"
            ) as mock_parser_cls:
                mock_parser = MagicMock()
                mock_parser.parse_mail.side_effect = [
                    (True, 101, 1),  # Changed, mail_id 101, conv_id 1
                    (False, 102, None),  # Not changed
                ]
                mock_parser_cls.return_value = mock_parser

                service = EmailSyncService(user_id=test_user)
                service.sync_emails()

                assert mock_parser.parse_mail.call_count == 2
                assert len(service.changed_conversation_ids) == 1
                assert service.changed_conversation_ids[0] == 1

    def test_sync_emails_handles_parser_errors(self, test_engine, test_user):
        """Test sync continues when parser raises exception."""
        with patch(
            "remail.interfaces.email.services.email_sync_service.ImapProtocol"
        ) as mock_imap_cls:
            mock_protocol = MagicMock()
            mock_protocol.fetch_emails.return_value = {
                1: {b"BODY[]": b"bad_email", b"FLAGS": []},
            }
            mock_protocol.serialize.return_value = '{"host": "imap.example.com"}'
            mock_imap_cls.return_value = mock_protocol

            with patch(
                "remail.interfaces.email.services.email_sync_service.EmailParser"
            ) as mock_parser_cls:
                mock_parser = MagicMock()
                mock_parser.parse_mail.side_effect = ValueError("Invalid email")
                mock_parser_cls.return_value = mock_parser

                service = EmailSyncService(user_id=test_user)
                service.sync_emails()  # Should not raise

                assert len(service.changed_conversation_ids) == 0

    def test_sync_emails_saves_connection_data(self, test_engine, test_user):
        """Test that sync saves updated connection data back to user."""
        with patch(
            "remail.interfaces.email.services.email_sync_service.ImapProtocol"
        ) as mock_imap_cls:
            mock_protocol = MagicMock()
            mock_protocol.fetch_emails.return_value = {}
            mock_protocol.serialize.return_value = '{"host": "updated.example.com", "port": 993}'
            mock_imap_cls.return_value = mock_protocol

            with patch("remail.interfaces.email.services.email_sync_service.EmailParser"):
                service = EmailSyncService(user_id=test_user)
                service.sync_emails()

                # Verify connection was updated
                with Session(test_engine) as session:
                    user = session.get(User, test_user)
                    assert "updated.example.com" in user.connection

    def test_check_for_changed_threads_empty(self, test_engine, test_user):
        """Test get_changed_conversations returns empty when no changes."""
        with patch("remail.interfaces.email.services.email_sync_service.ImapProtocol"):
            with patch("remail.interfaces.email.services.email_sync_service.EmailParser"):
                service = EmailSyncService(user_id=test_user)
                result = service.get_changed_conversations()

                assert result == []

    def test_check_for_changed_threads_returns_threads(self, test_engine, test_user):
        """Test get_changed_conversations returns conversations for changed emails."""
        with Session(test_engine) as session:
            user = session.get(User, test_user)
            from remail.models import Conversation

            conv = Conversation(type="conversation", user=user)
            session.add(conv)
            session.flush()
            conv_id = conv.id

            thread = Thread(title="Test Thread", conversation=conv)
            session.add(thread)
            session.flush()

            email1 = Email(
                message_id="<test1@example.com>",
                body="Body",
                sent_at="2024-01-01",
                imap_uid=100,
                thread=thread,
            )
            session.add(email1)
            session.commit()

        with patch("remail.interfaces.email.services.email_sync_service.ImapProtocol"):
            with patch("remail.interfaces.email.services.email_sync_service.EmailParser"):
                service = EmailSyncService(user_id=test_user)
                service.changed_conversation_ids = [conv_id]

                result = service.get_changed_conversations()

                assert len(result) == 1
                assert service.changed_conversation_ids == []  # Should be cleared after check

    @pytest.mark.asyncio
    async def test_wait_for_mail_changes_async(self, test_engine, test_user):
        """Test async waiting for mail changes."""
        with patch(
            "remail.interfaces.email.services.email_sync_service.ImapProtocol"
        ) as mock_imap_cls:
            mock_protocol = MagicMock()

            async def mock_wait():
                yield {1: {b"BODY[]": b"new_mail", b"FLAGS": []}}

            mock_protocol.wait_for_changes = mock_wait
            mock_protocol.serialize.return_value = '{"host": "imap.example.com"}'
            mock_imap_cls.return_value = mock_protocol

            with patch(
                "remail.interfaces.email.services.email_sync_service.EmailParser"
            ) as mock_parser_cls:
                mock_parser = MagicMock()
                mock_parser.parse_mail.return_value = (True, 200, 5)
                mock_parser_cls.return_value = mock_parser

                service = EmailSyncService(user_id=test_user)

                count = 0
                async for _ in service.wait_for_mail_changes_async():
                    count += 1
                    assert len(service.changed_conversation_ids) == 1
                    break  # Only test one iteration

                assert count == 1

    def test_email_exists_true(self, test_engine, test_user):
        """Test _email_exists returns True when email exists."""
        with Session(test_engine) as session:
            user = session.get(User, test_user)
            from remail.models import Conversation

            conv = Conversation(type="conversation", user=user)
            session.add(conv)
            session.flush()

            thread = Thread(title="Test", conversation=conv)
            session.add(thread)
            session.flush()

            email = Email(
                message_id="<exists@example.com>",
                subject="Test",
                body="Body",
                sent_at="2024-01-01",
                imap_uid=1,
                thread=thread,
            )
            session.add(email)
            session.commit()

        with patch("remail.interfaces.email.services.email_sync_service.ImapProtocol"):
            with patch("remail.interfaces.email.services.email_sync_service.EmailParser"):
                service = EmailSyncService(user_id=test_user)
                assert service._email_exists("<exists@example.com>") is True

    def test_email_exists_false(self, test_engine, test_user):
        """Test _email_exists returns False when email doesn't exist."""
        with patch("remail.interfaces.email.services.email_sync_service.ImapProtocol"):
            with patch("remail.interfaces.email.services.email_sync_service.EmailParser"):
                service = EmailSyncService(user_id=test_user)
                assert service._email_exists("<notexists@example.com>") is False

    def test_email_exists_empty_message_id(self, test_engine, test_user):
        """Test _email_exists returns False for empty message_id."""
        with patch("remail.interfaces.email.services.email_sync_service.ImapProtocol"):
            with patch("remail.interfaces.email.services.email_sync_service.EmailParser"):
                service = EmailSyncService(user_id=test_user)
                assert service._email_exists("") is False
                assert service._email_exists(None) is False
