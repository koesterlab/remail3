from datetime import UTC, datetime, timedelta

import pytest
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, select

from remail.enums import RecipientKind
from remail.models import Contact, Email, EmailReception, Thread


def test_thread_create(session: Session):
    """Test creating a basic thread."""
    thread = Thread()
    session.add(thread)
    session.commit()
    session.refresh(thread)

    assert thread.id is not None


def test_thread_auto_increment(session: Session):
    """Test that thread IDs auto-increment."""
    t1 = Thread()
    t2 = Thread()
    session.add(t1)
    session.add(t2)
    session.commit()
    session.refresh(t1)
    session.refresh(t2)

    assert t2.id > t1.id


def test_thread_with_single_message(session: Session):
    """Test thread with one email message."""
    sender = Contact(name="Sender", email_address="sender@example.com")
    session.add(sender)
    session.commit()

    thread = Thread()
    session.add(thread)
    session.commit()

    email = Email(
        subject="Test Email",
        body="Test Body",
        sent_at=datetime.now(UTC),
        sender_id=sender.id,
        thread_id=thread.id,
    )
    session.add(email)
    session.commit()
    session.refresh(thread)

    assert len(thread.messages) == 1
    assert thread.messages[0].subject == "Test Email"


def test_thread_with_multiple_messages(session: Session):
    """Test thread with multiple email messages."""
    sender = Contact(name="S", email_address="s@example.com")
    session.add(sender)
    session.commit()

    thread = Thread()
    session.add(thread)
    session.commit()

    e1 = Email(
        subject="First",
        body="Body1",
        sent_at=datetime.now(UTC),
        sender_id=sender.id,
        thread_id=thread.id,
    )
    e2 = Email(
        subject="Second",
        body="Body2",
        sent_at=datetime.now(UTC),
        sender_id=sender.id,
        thread_id=thread.id,
    )
    e3 = Email(
        subject="Third",
        body="Body3",
        sent_at=datetime.now(UTC),
        sender_id=sender.id,
        thread_id=thread.id,
    )
    session.add_all([e1, e2, e3])
    session.commit()
    session.refresh(thread)

    assert len(thread.messages) == 3
    assert {e.subject for e in thread.messages} == {"First", "Second", "Third"}


def test_thread_messages_ordering_by_sent_at(session: Session):
    """Test that messages can be ordered chronologically."""
    sender = Contact(name="S", email_address="s@example.com")
    session.add(sender)
    session.commit()

    thread = Thread()
    session.add(thread)
    session.commit()

    now = datetime.now(UTC)
    e1 = Email(
        subject="Oldest",
        body="B",
        sent_at=now - timedelta(days=2),
        sender_id=sender.id,
        thread_id=thread.id,
    )
    e2 = Email(
        subject="Middle",
        body="B",
        sent_at=now - timedelta(days=1),
        sender_id=sender.id,
        thread_id=thread.id,
    )
    e3 = Email(
        subject="Newest",
        body="B",
        sent_at=now,
        sender_id=sender.id,
        thread_id=thread.id,
    )
    session.add_all([e2, e3, e1])  # Add out of order
    session.commit()

    # Query messages in chronological order
    messages = session.exec(
        select(Email).where(Email.thread_id == thread.id).order_by(Email.sent_at)
    ).all()

    assert [m.subject for m in messages] == ["Oldest", "Middle", "Newest"]


def test_thread_relationship_back_to_emails(session: Session):
    """Test bidirectional relationship between Thread and Email."""
    sender = Contact(name="S", email_address="s@example.com")
    session.add(sender)
    session.commit()

    thread = Thread()
    session.add(thread)
    session.commit()

    email = Email(
        subject="Test",
        body="B",
        sent_at=datetime.now(UTC),
        sender_id=sender.id,
        thread_id=thread.id,
    )
    session.add(email)
    session.commit()
    session.refresh(email)
    session.refresh(thread)

    # Test thread -> messages
    assert thread.messages[0].id == email.id

    # Test email -> thread
    assert email.thread.id == thread.id


def test_thread_with_multiple_senders(session: Session):
    """Test thread with messages from different senders (conversation)."""
    s1 = Contact(name="Sender1", email_address="s1@example.com")
    s2 = Contact(name="Sender2", email_address="s2@example.com")
    session.add_all([s1, s2])
    session.commit()

    thread = Thread()
    session.add(thread)
    session.commit()

    e1 = Email(
        subject="Question",
        body="What's the status?",
        sent_at=datetime.now(UTC),
        sender_id=s1.id,
        thread_id=thread.id,
    )
    e2 = Email(
        subject="Re: Question",
        body="It's done!",
        sent_at=datetime.now(UTC),
        sender_id=s2.id,
        thread_id=thread.id,
    )
    session.add_all([e1, e2])
    session.commit()
    session.refresh(thread)

    senders = {msg.sender.email_address for msg in thread.messages}
    assert senders == {"s1@example.com", "s2@example.com"}


def test_thread_delete_with_emails_fails(session: Session):
    """Test that deleting a thread with emails fails due to NOT NULL constraint."""
    sender = Contact(name="S", email_address="s@example.com")
    session.add(sender)
    session.commit()

    thread = Thread()
    session.add(thread)
    session.commit()

    email = Email(
        subject="Test",
        body="B",
        sent_at=datetime.now(UTC),
        sender_id=sender.id,
        thread_id=thread.id,
    )
    session.add(email)
    session.commit()

    # Delete the thread should fail because email.thread_id is NOT NULL
    session.delete(thread)
    with pytest.raises(IntegrityError):
        session.commit()


def test_thread_query_by_id(session: Session):
    """Test querying threads by ID."""
    t1 = Thread()
    t2 = Thread()
    session.add_all([t1, t2])
    session.commit()

    found = session.exec(select(Thread).where(Thread.id == t1.id)).first()

    assert found is not None
    assert found.id == t1.id


def test_thread_count_messages(session: Session):
    """Test counting messages in a thread."""
    sender = Contact(name="S", email_address="s@example.com")
    session.add(sender)
    session.commit()

    thread = Thread()
    session.add(thread)
    session.commit()

    # Add 5 messages
    for i in range(5):
        email = Email(
            subject=f"Message {i}",
            body="B",
            sent_at=datetime.now(UTC),
            sender_id=sender.id,
            thread_id=thread.id,
        )
        session.add(email)
    session.commit()
    session.refresh(thread)

    assert len(thread.messages) == 5


def test_thread_with_recipients(session: Session):
    """Test that thread emails can have recipients."""
    sender = Contact(name="S", email_address="s@example.com")
    r1 = Contact(name="R1", email_address="r1@example.com")
    r2 = Contact(name="R2", email_address="r2@example.com")
    session.add_all([sender, r1, r2])
    session.commit()

    thread = Thread()
    session.add(thread)
    session.commit()

    email = Email(
        subject="Group Email",
        body="B",
        sent_at=datetime.now(UTC),
        sender_id=sender.id,
        thread_id=thread.id,
    )
    session.add(email)
    session.commit()
    session.refresh(email)

    rec1 = EmailReception(kind=RecipientKind.TO, email_id=email.id, contact_id=r1.id)
    rec2 = EmailReception(kind=RecipientKind.CC, email_id=email.id, contact_id=r2.id)
    session.add_all([rec1, rec2])
    session.commit()
    session.refresh(thread)

    # Access recipients through thread messages
    recipients = {rec.contact.email_address for rec in thread.messages[0].recipients}
    assert recipients == {"r1@example.com", "r2@example.com"}


def test_thread_empty_messages(session: Session):
    """Test that a thread can exist without messages."""
    thread = Thread()
    session.add(thread)
    session.commit()
    session.refresh(thread)

    assert len(thread.messages) == 0


def test_thread_get_latest_message(session: Session):
    """Test getting the most recent message in a thread."""
    sender = Contact(name="S", email_address="s@example.com")
    session.add(sender)
    session.commit()

    thread = Thread()
    session.add(thread)
    session.commit()

    now = datetime.now(UTC)
    e1 = Email(
        subject="Old",
        body="B",
        sent_at=now - timedelta(hours=2),
        sender_id=sender.id,
        thread_id=thread.id,
    )
    e2 = Email(
        subject="Recent",
        body="B",
        sent_at=now,
        sender_id=sender.id,
        thread_id=thread.id,
    )
    session.add_all([e1, e2])
    session.commit()

    # Get latest message
    latest = session.exec(
        select(Email).where(Email.thread_id == thread.id).order_by(Email.sent_at.desc())
    ).first()

    assert latest is not None
    assert latest.subject == "Recent"


def test_thread_query_threads_with_message_count(session: Session):
    """Test querying threads and counting their messages."""
    sender = Contact(name="S", email_address="s@example.com")
    session.add(sender)
    session.commit()

    # Create thread with 3 messages
    t1 = Thread()
    session.add(t1)
    session.commit()

    for i in range(3):
        session.add(
            Email(
                subject=f"T1-{i}",
                body="B",
                sent_at=datetime.now(UTC),
                sender_id=sender.id,
                thread_id=t1.id,
            )
        )

    # Create thread with 1 message
    t2 = Thread()
    session.add(t2)
    session.commit()

    session.add(
        Email(
            subject="T2-0",
            body="B",
            sent_at=datetime.now(UTC),
            sender_id=sender.id,
            thread_id=t2.id,
        )
    )

    session.commit()

    # Query all threads
    threads = session.exec(select(Thread)).all()
    message_counts = {t.id: len(t.messages) for t in threads}

    assert message_counts[t1.id] == 3
    assert message_counts[t2.id] == 1


def test_thread_update_not_applicable(session: Session):
    """Test that threads don't have updatable fields beyond ID."""
    thread = Thread()
    session.add(thread)
    session.commit()
    session.refresh(thread)

    original_id = thread.id

    # Thread has no other fields to update, verify ID remains stable
    session.refresh(thread)
    assert thread.id == original_id
