from datetime import UTC, datetime, timedelta

from sqlmodel import Session, select

from remail.enums import RecipientKind
from remail.models import Attachment, Contact, Conversation, Email, EmailReception, Thread


def _create_thread(session: Session, title: str | None = None) -> Thread:
    conversation = Conversation(custom_name="C")
    session.add(conversation)
    session.commit()
    thread = Thread(title=title or "", conversation_id=conversation.id)
    session.add(thread)
    session.commit()
    session.refresh(thread)
    return thread


def test_email_create(session: Session):
    sender = Contact(name="S", email_address="s@example.com")
    session.add(sender)
    session.commit()

    thread = _create_thread(session)

    e = Email(
        message_id="Hello",
        body="Body",
        sent_at=datetime.now(UTC),
        sender_id=sender.id,
        thread_id=thread.id,
    )
    session.add(e)
    session.commit()
    session.refresh(e)

    assert e.id is not None
    assert e.sender_id == sender.id
    assert e.thread_id == thread.id


def test_email_auto_increment(session: Session):
    s = Contact(name="S", email_address="s@example.com")
    session.add(s)
    session.commit()

    thread = _create_thread(session)

    e1 = Email(
        message_id="1", body="B", sent_at=datetime.now(UTC), sender_id=s.id, thread_id=thread.id
    )
    e2 = Email(
        message_id="2", body="B", sent_at=datetime.now(UTC), sender_id=s.id, thread_id=thread.id
    )
    session.add(e1)
    session.add(e2)
    session.commit()
    session.refresh(e1)
    session.refresh(e2)

    assert e2.id > e1.id


def test_email_relationship_to_sender(session: Session):
    s = Contact(name="Sender", email_address="sender@example.com")
    session.add(s)
    session.commit()

    thread = _create_thread(session)

    e = Email(
        message_id="Hi", body="B", sent_at=datetime.now(UTC), sender_id=s.id, thread_id=thread.id
    )
    session.add(e)
    session.commit()
    session.refresh(e)
    session.refresh(s)

    assert e.sender.id == s.id
    assert s.sent_emails[0].id == e.id


def test_email_with_attachments(session: Session):
    s = Contact(name="S", email_address="s@example.com")
    session.add(s)
    session.commit()

    thread = _create_thread(session)

    e = Email(
        message_id="A", body="B", sent_at=datetime.now(UTC), sender_id=s.id, thread_id=thread.id
    )
    session.add(e)
    session.commit()
    session.refresh(e)

    a1 = Attachment(filename="f1.txt", email_id=e.id)
    a2 = Attachment(filename="f2.txt", email_id=e.id)
    session.add(a1)
    session.add(a2)
    session.commit()
    session.refresh(e)

    assert {a.filename for a in e.attachments} == {"f1.txt", "f2.txt"}


def test_email_with_recipients(session: Session):
    s = Contact(name="S", email_address="s@example.com")
    r1 = Contact(name="R1", email_address="r1@example.com")
    r2 = Contact(name="R2", email_address="r2@example.com")
    session.add(s)
    session.add(r1)
    session.add(r2)
    session.commit()

    thread = _create_thread(session)

    e = Email(
        message_id="X", body="B", sent_at=datetime.now(UTC), sender_id=s.id, thread_id=thread.id
    )
    session.add(e)
    session.commit()
    session.refresh(e)

    to = EmailReception(kind=RecipientKind.TO, email_id=e.id, contact_id=r1.id)
    cc = EmailReception(kind=RecipientKind.CC, email_id=e.id, contact_id=r2.id)
    session.add(to)
    session.add(cc)
    session.commit()
    session.refresh(e)

    kinds = {rec.kind for rec in e.recipients}
    assert kinds == {RecipientKind.TO, RecipientKind.CC}


def test_email_cascade_delete_attachments(session: Session):
    s = Contact(name="S", email_address="s@example.com")
    session.add(s)
    session.commit()

    thread = _create_thread(session)

    e = Email(
        message_id="Cas", body="B", sent_at=datetime.now(UTC), sender_id=s.id, thread_id=thread.id
    )
    session.add(e)
    session.commit()
    session.refresh(e)

    a = Attachment(filename="dead.txt", email_id=e.id)
    session.add(a)
    session.commit()
    session.delete(e)
    session.commit()

    assert session.exec(select(Attachment).where(Attachment.filename == "dead.txt")).first() is None


def test_email_cascade_delete_recipients(session: Session):
    s = Contact(name="S", email_address="s@example.com")
    r = Contact(name="R", email_address="r@example.com")
    session.add(s)
    session.add(r)
    session.commit()

    thread = _create_thread(session)

    e = Email(
        message_id="Cas2", body="B", sent_at=datetime.now(UTC), sender_id=s.id, thread_id=thread.id
    )
    session.add(e)
    session.commit()
    session.refresh(e)

    rec = EmailReception(kind=RecipientKind.TO, email_id=e.id, contact_id=r.id)
    session.add(rec)
    session.commit()
    session.delete(e)
    session.commit()

    assert (
        session.exec(
            select(EmailReception).where(
                EmailReception.email_id == e.id, EmailReception.contact_id == r.id
            )
        ).first()
        is None
    )


def test_email_query_by_message_id_sender_and_date(session: Session):
    s = Contact(name="S", email_address="s@example.com")
    session.add(s)
    session.commit()

    thread = _create_thread(session)

    now = datetime.now(UTC)
    e1 = Email(
        message_id="Alpha",
        body="B",
        sent_at=now - timedelta(days=1),
        sender_id=s.id,
        thread_id=thread.id,
    )
    e2 = Email(message_id="Beta", body="B", sent_at=now, sender_id=s.id, thread_id=thread.id)
    session.add(e1)
    session.add(e2)
    session.commit()

    got = session.exec(select(Email).where(Email.message_id == "Alpha")).first()
    assert got and got.id == e1.id

    got2 = session.exec(select(Email).where(Email.sender_id == s.id)).all()
    assert {e.message_id for e in got2} == {"Alpha", "Beta"}

    got3 = session.exec(select(Email).where(Email.sent_at >= now - timedelta(hours=12))).all()

    assert [e.message_id for e in got3] == ["Beta"]


def test_email_update(session: Session):
    s = Contact(name="S", email_address="s@example.com")
    session.add(s)
    session.commit()

    thread = _create_thread(session)

    e = Email(
        message_id="Old",
        body="Old body",
        sent_at=datetime.now(UTC),
        sender_id=s.id,
        thread_id=thread.id,
    )
    session.add(e)
    session.commit()
    session.refresh(e)

    e.message_id = "New"
    e.body = "New body"
    session.add(e)
    session.commit()
    session.refresh(e)

    assert e.message_id == "New" and e.body == "New body"
