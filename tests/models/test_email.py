from datetime import UTC, datetime, timedelta

from sqlmodel import Session, select

from remail.enums import RecipientKind
from remail.models import Attachment, Contact, Email, EmailReception


def test_email_create(session: Session):
    sender = Contact(name="S", email_address="s@example.com")
    session.add(sender)
    session.commit()

    e = Email(subject="Hello", body="Body", sent_at=datetime.now(UTC), sender_id=sender.id)
    session.add(e)
    session.commit()
    session.refresh(e)

    assert e.id is not None
    assert e.sender_id == sender.id


def test_email_auto_increment(session: Session):
    s = Contact(name="S", email_address="s@example.com")
    session.add(s)
    session.commit()

    e1 = Email(subject="1", body="B", sent_at=datetime.now(UTC), sender_id=s.id)
    e2 = Email(subject="2", body="B", sent_at=datetime.now(UTC), sender_id=s.id)
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

    e = Email(subject="Hi", body="B", sent_at=datetime.now(UTC), sender_id=s.id)
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

    e = Email(subject="A", body="B", sent_at=datetime.now(UTC), sender_id=s.id)
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

    e = Email(subject="X", body="B", sent_at=datetime.now(UTC), sender_id=s.id)
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

    e = Email(subject="Cas", body="B", sent_at=datetime.now(UTC), sender_id=s.id)
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

    e = Email(subject="Cas2", body="B", sent_at=datetime.now(UTC), sender_id=s.id)
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


def test_email_query_by_subject_sender_and_date(session: Session):
    s = Contact(name="S", email_address="s@example.com")
    session.add(s)
    session.commit()

    now = datetime.now(UTC)
    e1 = Email(subject="Alpha", body="B", sent_at=now - timedelta(days=1), sender_id=s.id)
    e2 = Email(subject="Beta", body="B", sent_at=now, sender_id=s.id)
    session.add(e1)
    session.add(e2)
    session.commit()

    got = session.exec(select(Email).where(Email.subject == "Alpha")).first()
    assert got and got.id == e1.id

    got2 = session.exec(select(Email).where(Email.sender_id == s.id)).all()
    assert {e.subject for e in got2} == {"Alpha", "Beta"}

    got3 = session.exec(select(Email).where(Email.sent_at >= now - timedelta(hours=12))).all()

    assert [e.subject for e in got3] == ["Beta"]


def test_email_update(session: Session):
    s = Contact(name="S", email_address="s@example.com")
    session.add(s)
    session.commit()

    e = Email(subject="Old", body="Old body", sent_at=datetime.now(UTC), sender_id=s.id)
    session.add(e)
    session.commit()
    session.refresh(e)

    e.subject = "New"
    e.body = "New body"
    session.add(e)
    session.commit()
    session.refresh(e)

    assert e.subject == "New" and e.body == "New body"
