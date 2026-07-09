from datetime import UTC, datetime

from sqlmodel import Session, select

from remail.models import Attachment, Contact, Conversation, Email, Thread


def _create_thread(session: Session) -> Thread:
    conversation = Conversation(custom_name="C")
    session.add(conversation)
    session.commit()
    thread = Thread(conversation_id=conversation.id)
    session.add(thread)
    session.commit()
    session.refresh(thread)
    return thread


def test_attachment_create(session: Session):
    c = Contact(name="S", email_address="s@example.com")
    session.add(c)
    session.commit()

    thread = _create_thread(session)

    e = Email(
        message_id="Attach",
        body="B",
        sent_at=datetime.now(UTC),
        sender_id=c.id,
        thread_id=thread.id,
    )
    session.add(e)
    session.commit()
    session.refresh(e)

    a = Attachment(filename="file.txt", email_id=e.id)
    session.add(a)
    session.commit()
    session.refresh(a)

    assert a.id is not None
    assert a.email_id == e.id


def test_attachment_auto_increment(session: Session):
    c = Contact(name="S", email_address="s@example.com")
    session.add(c)
    session.commit()

    thread = _create_thread(session)

    e = Email(
        message_id="Attach2",
        body="B",
        sent_at=datetime.now(UTC),
        sender_id=c.id,
        thread_id=thread.id,
    )
    session.add(e)
    session.commit()
    session.refresh(e)

    a1 = Attachment(filename="1.txt", email_id=e.id)
    a2 = Attachment(filename="2.txt", email_id=e.id)
    session.add(a1)
    session.add(a2)
    session.commit()

    session.refresh(a1)
    session.refresh(a2)

    assert a2.id > a1.id


def test_attachment_relationship_to_email(session: Session):
    c = Contact(name="S", email_address="s@example.com")
    session.add(c)
    session.commit()

    thread = _create_thread(session)

    e = Email(
        message_id="Attach3",
        body="B",
        sent_at=datetime.now(UTC),
        sender_id=c.id,
        thread_id=thread.id,
    )
    session.add(e)
    session.commit()
    session.refresh(e)

    a = Attachment(filename="f.txt", email_id=e.id)
    session.add(a)
    session.commit()
    session.refresh(a)

    assert a.email.id == e.id
    assert e.attachments[0].filename == "f.txt"


def test_attachment_query(session: Session):
    c = Contact(name="S", email_address="s@example.com")
    session.add(c)
    session.commit()

    thread = _create_thread(session)

    e = Email(
        message_id="AttachQ",
        body="B",
        sent_at=datetime.now(UTC),
        sender_id=c.id,
        thread_id=thread.id,
    )
    session.add(e)
    session.commit()
    session.refresh(e)

    a = Attachment(filename="q.txt", email_id=e.id)
    session.add(a)
    session.commit()

    got = session.exec(select(Attachment).where(Attachment.filename == "q.txt")).first()

    assert got is not None
