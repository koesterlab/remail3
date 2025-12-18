from datetime import UTC, datetime

from sqlmodel import Session, select

from remail.enums import RecipientKind
from remail.models import Contact, Email, EmailReception, Thread


def test_contact_create(session: Session):
    c = Contact(name="John Doe", email_address="john@example.com")
    session.add(c)
    session.commit()
    session.refresh(c)

    assert c.id is not None
    assert c.email_address == "john@example.com"


def test_contact_auto_increment(session: Session):
    c1 = Contact(name="A", email_address="a@example.com")
    c2 = Contact(name="B", email_address="b@example.com")
    session.add(c1)
    session.add(c2)
    session.commit()
    session.refresh(c1)
    session.refresh(c2)

    assert c2.id > c1.id


def test_contact_relationship_sent_emails(session: Session):
    sender = Contact(name="Sender", email_address="sender@example.com")
    session.add(sender)
    session.commit()
    session.refresh(sender)

    thread = Thread()
    session.add(thread)
    session.commit()

    e1 = Email(
        subject="S1", body="B1", sent_at=datetime.now(UTC), sender_id=sender.id, thread_id=thread.id
    )
    e2 = Email(
        subject="S2", body="B2", sent_at=datetime.now(UTC), sender_id=sender.id, thread_id=thread.id
    )
    session.add(e1)
    session.add(e2)
    session.commit()
    session.refresh(sender)

    assert {e.subject for e in sender.sent_emails} == {"S1", "S2"}


def test_contact_relationship_receptions(session: Session):
    sender = Contact(name="S", email_address="s@example.com")
    recipient = Contact(name="R", email_address="r@example.com")
    session.add(sender)
    session.add(recipient)
    session.commit()

    thread = Thread()
    session.add(thread)
    session.commit()

    email = Email(
        subject="Hi", body="B", sent_at=datetime.now(UTC), sender_id=sender.id, thread_id=thread.id
    )
    session.add(email)
    session.commit()
    session.refresh(email)

    rec = EmailReception(kind=RecipientKind.TO, email_id=email.id, contact_id=recipient.id)
    session.add(rec)
    session.commit()
    session.refresh(recipient)

    assert len(recipient.receptions) == 1
    assert recipient.receptions[0].email.subject == "Hi"
    assert recipient.receptions[0].kind == RecipientKind.TO


def test_contact_query_by_email(session: Session):
    c = Contact(name="Alice", email_address="alice@example.com")
    session.add(c)
    session.commit()

    got = session.exec(select(Contact).where(Contact.email_address == "alice@example.com")).first()

    assert got and got.name == "Alice"


def test_contact_query_by_name(session: Session):
    c = Contact(name="Bob Jones", email_address="bob@example.com")
    session.add(c)
    session.commit()

    got = session.exec(select(Contact).where(Contact.name == "Bob Jones")).first()

    assert got and got.email_address == "bob@example.com"


def test_contact_update(session: Session):
    c = Contact(name="Temp", email_address="temp@example.com")
    session.add(c)
    session.commit()
    session.refresh(c)

    c.name = "Temp Updated"
    c.email_address = "temp2@example.com"
    session.add(c)
    session.commit()
    session.refresh(c)

    assert c.name == "Temp Updated"
    assert c.email_address == "temp2@example.com"


def test_contact_delete_without_emails(session: Session):
    c = Contact(name="Temp", email_address="del@example.com")
    session.add(c)
    session.commit()

    cid = c.id
    session.delete(c)
    session.commit()

    assert session.exec(select(Contact).where(Contact.id == cid)).first() is None
