"""Tests for DashboardService."""

from datetime import datetime

from sqlmodel import Session

from remail.enums import Protocol
from remail.interfaces.email.services.dashboard_service import DashboardService
from remail.models import Contact, Conversation, Email, Thread, User


class TestDashboardService:
    """Test suite for DashboardService."""

    def test_get_recent_emails_for_user_empty(self, test_engine):
        """Test get_recent_emails_for_user returns empty list when no emails."""
        with Session(test_engine) as session:
            user = User(
                name="test",
                email="test@example.com",
                protocol=Protocol.IMAP,
                connection='{"host": "imap.example.com"}',
            )
            session.add(user)
            session.commit()
            session.refresh(user)
            user_id = user.id

        result = DashboardService.get_recent_emails_for_user(user_id)

        assert isinstance(result, list)
        assert len(result) == 0

    def test_get_recent_emails_for_user_returns_emails(self, test_engine):
        """Test get_recent_emails_for_user returns emails for user."""
        with Session(test_engine) as session:
            # Create user
            user = User(
                name="test",
                email="test@example.com",
                protocol=Protocol.IMAP,
                connection='{"host": "imap.example.com"}',
            )
            session.add(user)
            session.flush()

            # Create sender contact
            sender = Contact(
                name="Sender",
                email_address="sender@example.com",
                is_known=True,
            )
            session.add(sender)
            session.flush()

            # Create conversation
            conv = Conversation(type="conversation", user=user)
            session.add(conv)
            session.flush()

            # Create thread
            thread = Thread(title="Test Thread", conversation=conv)
            session.add(thread)
            session.flush()

            # Create email
            email = Email(
                message_id="<test@example.com>",
                subject="Test Email",
                body="Test Body",
                sent_at=datetime(2024, 1, 1),
                imap_uid=1,
                sender=sender,
                thread=thread,
            )
            session.add(email)
            session.commit()
            user_id = user.id

        result = DashboardService.get_recent_emails_for_user(user_id)

        assert len(result) == 1
        email_result, contact_result = result[0]
        assert email_result.subject == "Test Email"
        assert contact_result.email_address == "sender@example.com"

    def test_get_recent_emails_for_user_respects_limit(self, test_engine):
        """Test get_recent_emails_for_user respects limit parameter."""
        with Session(test_engine) as session:
            user = User(
                name="test",
                email="test@example.com",
                protocol=Protocol.IMAP,
                connection='{"host": "imap.example.com"}',
            )
            session.add(user)
            session.flush()

            sender = Contact(
                name="Sender",
                email_address="sender@example.com",
                is_known=True,
            )
            session.add(sender)
            session.flush()

            conv = Conversation(type="conversation", user=user)
            session.add(conv)
            session.flush()

            thread = Thread(title="Test Thread", conversation=conv)
            session.add(thread)
            session.flush()

            # Create 10 emails
            for i in range(10):
                email = Email(
                    message_id=f"<test{i}@example.com>",
                    subject=f"Email {i}",
                    body="Body",
                    sent_at=datetime(2024, 1, i + 1),
                    imap_uid=i + 1,
                    sender=sender,
                    thread=thread,
                )
                session.add(email)

            session.commit()
            user_id = user.id

        # Request only 3 emails
        result = DashboardService.get_recent_emails_for_user(user_id, limit=3)

        assert len(result) == 3

    def test_get_recent_emails_for_user_orders_by_sent_at_desc(self, test_engine):
        """Test get_recent_emails_for_user returns most recent emails first."""
        with Session(test_engine) as session:
            user = User(
                name="test",
                email="test@example.com",
                protocol=Protocol.IMAP,
                connection='{"host": "imap.example.com"}',
            )
            session.add(user)
            session.flush()

            sender = Contact(
                name="Sender",
                email_address="sender@example.com",
                is_known=True,
            )
            session.add(sender)
            session.flush()

            conv = Conversation(type="conversation", user=user)
            session.add(conv)
            session.flush()

            thread = Thread(title="Test Thread", conversation=conv)
            session.add(thread)
            session.flush()

            # Create emails with different timestamps
            email1 = Email(
                message_id="<old@example.com>",
                subject="Old Email",
                body="Body",
                sent_at=datetime(2024, 1, 1),
                imap_uid=1,
                sender=sender,
                thread=thread,
            )
            email2 = Email(
                message_id="<recent@example.com>",
                subject="Recent Email",
                body="Body",
                sent_at=datetime(2024, 1, 10),
                imap_uid=2,
                sender=sender,
                thread=thread,
            )
            email3 = Email(
                message_id="<newest@example.com>",
                subject="Newest Email",
                body="Body",
                sent_at=datetime(2024, 1, 15),
                imap_uid=3,
                sender=sender,
                thread=thread,
            )
            session.add_all([email1, email2, email3])
            session.commit()
            user_id = user.id

        result = DashboardService.get_recent_emails_for_user(user_id, limit=5)

        assert len(result) == 3
        # Should be ordered by most recent first
        assert result[0][0].subject == "Newest Email"
        assert result[1][0].subject == "Recent Email"
        assert result[2][0].subject == "Old Email"

    def test_get_recent_emails_for_user_isolates_users(self, test_engine):
        """Test get_recent_emails_for_user only returns emails for specific user."""
        with Session(test_engine) as session:
            # Create two users
            user1 = User(
                name="user1",
                email="user1@example.com",
                protocol=Protocol.IMAP,
                connection='{"host": "imap.example.com"}',
            )
            user2 = User(
                name="user2",
                email="user2@example.com",
                protocol=Protocol.IMAP,
                connection='{"host": "imap.example.com"}',
            )
            session.add_all([user1, user2])
            session.flush()

            sender = Contact(
                name="Sender",
                email_address="sender@example.com",
                is_known=True,
            )
            session.add(sender)
            session.flush()

            # Create conversation for user1
            conv1 = Conversation(type="conversation", user=user1)
            session.add(conv1)
            session.flush()

            thread1 = Thread(title="User1 Thread", conversation=conv1)
            session.add(thread1)
            session.flush()

            email1 = Email(
                message_id="<user1@example.com>",
                subject="User1 Email",
                body="Body",
                sent_at=datetime(2024, 1, 1),
                imap_uid=1,
                sender=sender,
                thread=thread1,
            )
            session.add(email1)

            # Create conversation for user2
            conv2 = Conversation(type="conversation", user=user2)
            session.add(conv2)
            session.flush()

            thread2 = Thread(title="User2 Thread", conversation=conv2)
            session.add(thread2)
            session.flush()

            email2 = Email(
                message_id="<user2@example.com>",
                subject="User2 Email",
                body="Body",
                sent_at=datetime(2024, 1, 1),
                imap_uid=2,
                sender=sender,
                thread=thread2,
            )
            session.add(email2)

            session.commit()
            user1_id = user1.id
            user2_id = user2.id

        # Get emails for user1
        result1 = DashboardService.get_recent_emails_for_user(user1_id)
        assert len(result1) == 1
        assert result1[0][0].subject == "User1 Email"

        # Get emails for user2
        result2 = DashboardService.get_recent_emails_for_user(user2_id)
        assert len(result2) == 1
        assert result2[0][0].subject == "User2 Email"

    def test_get_recent_appointment_items_for_user_returns_empty(self, test_engine):
        """Test get_recent_appointment_items_for_user returns empty list (not implemented)."""
        with Session(test_engine) as session:
            user = User(
                name="test",
                email="test@example.com",
                protocol=Protocol.IMAP,
                connection='{"host": "imap.example.com"}',
            )
            session.add(user)
            session.commit()
            user_id = user.id

        result = DashboardService.get_recent_appointment_items_for_user(user_id)

        # Currently returns empty list (not implemented)
        assert isinstance(result, list)
        assert len(result) == 0
