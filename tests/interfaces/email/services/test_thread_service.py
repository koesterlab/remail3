"""Tests for ThreadService."""

from datetime import datetime

import pytest
from sqlmodel import Session

from remail.enums import Protocol
from remail.interfaces.email.services.thread_service import ThreadService
from remail.models import Contact, Conversation, Email, Thread, User


@pytest.fixture
def test_user(test_engine):
    """Create a test user in the database."""
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
        return user.id


@pytest.fixture
def test_conversation(test_engine, test_user):
    """Create a test conversation."""
    with Session(test_engine) as session:
        user = session.get(User, test_user)
        conv = Conversation(type="conversation", user=user)
        session.add(conv)
        session.commit()
        session.refresh(conv)
        return conv.id


@pytest.fixture
def test_sender(test_engine):
    """Create a sender contact for email tests."""
    with Session(test_engine) as session:
        sender = Contact(
            name="Sender",
            email_address="sender@example.com",
            first_name="Sender",
            last_name="Test",
        )
        session.add(sender)
        session.commit()
        session.refresh(sender)
        return sender.id


class TestThreadService:
    """Test suite for ThreadService."""

    def test_get_thread_by_id_found(self, test_engine, test_conversation):
        """Test get_thread_by_id returns thread when found."""
        with Session(test_engine) as session:
            thread = Thread(title="Test Thread", conversation_id=test_conversation)
            session.add(thread)
            session.commit()
            session.refresh(thread)
            thread_id = thread.id

        service = ThreadService()
        result = service.get_thread_by_id(thread_id)

        assert result is not None
        assert result.id == thread_id
        assert result.title == "Test Thread"

    def test_get_thread_by_id_not_found(self):
        """Test get_thread_by_id returns None when not found."""
        service = ThreadService()
        result = service.get_thread_by_id(99999)

        assert result is None

    def test_create_thread(self, test_engine, test_conversation):
        """Test create_thread creates new thread."""
        service = ThreadService()
        result = service.create_thread(title="New Thread", conversation_id=test_conversation)

        assert result is not None
        assert result.id is not None
        assert result.title == "New Thread"
        assert result.conversation_id == test_conversation

        # Verify thread was saved
        with Session(test_engine) as session:
            saved = session.get(Thread, result.id)
            assert saved is not None
            assert saved.title == "New Thread"

    def test_normalize_subject_removes_re_prefix(self):
        """Test normalize_subject removes 'Re:' prefix."""
        service = ThreadService()

        assert service.normalize_subject("Re: Test Subject") == "Test Subject"
        assert service.normalize_subject("RE: Test Subject") == "Test Subject"
        assert service.normalize_subject("re: Test Subject") == "Test Subject"

    def test_normalize_subject_removes_fw_prefix(self):
        """Test normalize_subject removes 'Fw:' and 'Fwd:' prefixes."""
        service = ThreadService()

        assert service.normalize_subject("Fw: Test Subject") == "Test Subject"
        assert service.normalize_subject("Fwd: Test Subject") == "Test Subject"
        assert service.normalize_subject("FWD: Test Subject") == "Test Subject"

    def test_normalize_subject_removes_multiple_prefixes(self):
        """Test normalize_subject removes multiple nested prefixes."""
        service = ThreadService()

        assert service.normalize_subject("Re: Fw: Test Subject") == "Test Subject"
        assert service.normalize_subject("Fwd: Re: Fwd: Test") == "Test"

    def test_normalize_subject_removes_german_prefixes(self):
        """Test normalize_subject removes German 'AW:' prefix."""
        service = ThreadService()

        assert service.normalize_subject("AW: Test Subject") == "Test Subject"
        assert service.normalize_subject("aw: Test Subject") == "Test Subject"

    def test_normalize_subject_empty_string(self):
        """Test normalize_subject handles empty string."""
        service = ThreadService()

        assert service.normalize_subject("") == ""

    def test_normalize_subject_only_prefix(self):
        """Test normalize_subject handles subject with only prefix."""
        service = ThreadService()

        assert service.normalize_subject("Re: ") == ""
        assert service.normalize_subject("Re:") == ""

    def test_normalize_subject_no_prefix(self):
        """Test normalize_subject returns unchanged when no prefix."""
        service = ThreadService()

        assert service.normalize_subject("Test Subject") == "Test Subject"
        assert service.normalize_subject("Meeting Tomorrow") == "Meeting Tomorrow"

    def test_organize_email_into_thread_creates_new_thread(
        self, test_engine, test_conversation, test_sender
    ):
        """Test organize_email_into_thread creates new thread for new subject."""
        with Session(test_engine) as session:
            conv = session.get(Conversation, test_conversation)

            email = Email(
                message_id="<test@example.com>",
                subject="New Subject",
                body="Body",
                sent_at=datetime(2024, 1, 1),
                imap_uid=1,
                sender_id=test_sender,
            )
            session.add(email)
            session.flush()

            service = ThreadService()
            service.organize_email_into_thread(email, "New Subject", conv, session)
            session.commit()

            # Verify new thread was created
            threads = conv.threads
            assert len(threads) == 1
            assert threads[0].title == "New Subject"
            assert email.thread == threads[0]

    def test_organize_email_into_thread_uses_existing_thread(
        self, test_engine, test_conversation, test_sender
    ):
        """Test organize_email_into_thread uses existing thread for same subject."""
        with Session(test_engine) as session:
            conv = session.get(Conversation, test_conversation)

            # Create existing thread
            existing_thread = Thread(title="Existing Subject", conversation=conv, unread_count=0)
            session.add(existing_thread)
            session.flush()

            # Create new email with same subject
            email = Email(
                message_id="<test2@example.com>",
                subject="Re: Existing Subject",
                body="Reply",
                sent_at=datetime(2024, 1, 2),
                imap_uid=2,
                sender_id=test_sender,
            )
            session.add(email)
            session.flush()

            service = ThreadService()
            service.organize_email_into_thread(email, "Re: Existing Subject", conv, session)
            session.commit()

            # Verify email was added to existing thread
            assert email.thread == existing_thread
            assert len(conv.threads) == 1  # Only one thread

    def test_organize_email_into_thread_normalizes_subject(
        self, test_engine, test_conversation, test_sender
    ):
        """Test organize_email_into_thread normalizes subject before matching."""
        with Session(test_engine) as session:
            conv = session.get(Conversation, test_conversation)

            thread1 = Thread(title="Test Subject", conversation=conv, unread_count=0)
            session.add(thread1)
            session.flush()

            email = Email(
                message_id="<test3@example.com>",
                subject="Re: Fw: Test Subject",
                body="Reply",
                sent_at=datetime(2024, 1, 3),
                imap_uid=3,
                sender_id=test_sender,
            )
            session.add(email)
            session.flush()

            service = ThreadService()
            service.organize_email_into_thread(email, "Re: Fw: Test Subject", conv, session)
            session.commit()

            # Should match despite different prefixes
            assert email.thread == thread1

    def test_organize_email_into_thread_updates_unread_count(
        self, test_engine, test_conversation, test_sender
    ):
        """Test organize_email_into_thread increments unread count for unread emails."""
        with Session(test_engine) as session:
            conv = session.get(Conversation, test_conversation)

            thread = Thread(title="Test", conversation=conv, unread_count=0)
            session.add(thread)
            session.flush()

            email = Email(
                message_id="<test4@example.com>",
                subject="Test",
                body="Body",
                sent_at=datetime(2024, 1, 4),
                imap_uid=4,
                read=False,
                sender_id=test_sender,
            )
            session.add(email)
            session.flush()

            service = ThreadService()
            service.organize_email_into_thread(email, "Test", conv, session)
            session.commit()
            session.refresh(thread)

            assert thread.unread_count == 1

    def test_get_most_important_threads(self, test_engine, test_conversation):
        """Test get_most_important_threads returns threads ordered by time."""
        with Session(test_engine) as session:
            conv = session.get(Conversation, test_conversation)

            from datetime import datetime

            thread1 = Thread(
                title="Old Thread",
                conversation=conv,
                last_message_time=datetime(2024, 1, 1),
            )
            thread2 = Thread(
                title="Recent Thread",
                conversation=conv,
                last_message_time=datetime(2024, 1, 10),
            )
            thread3 = Thread(
                title="Newest Thread",
                conversation=conv,
                last_message_time=datetime(2024, 1, 15),
            )
            session.add_all([thread1, thread2, thread3])
            session.commit()

        service = ThreadService()
        result = service.get_most_important_threads(count=2)

        assert len(result) == 2
        # Should be ordered by most recent first
        assert result[0][0].title == "Newest Thread"
        assert result[1][0].title == "Recent Thread"

    def test_get_most_important_threads_default_count(self, test_engine, test_conversation):
        """Test get_most_important_threads uses default count of 5."""
        service = ThreadService()
        result = service.get_most_important_threads()

        assert isinstance(result, list)
        assert len(result) <= 5
