from datetime import UTC, datetime

import pytest
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, select

from remail.enums import RecipientKind
from remail.models import Contact, Email, EmailReception


def test_email_reception_create(session: Session):
    s = Contact(name="S", email_address="s@example.com")
    r = Contact(name="R", email_address="r@example.com")
    session.add(s)
    session.add(r)
    session.commit()

    e = Email(subject="Hello", body="B", sent_at=datetime.now(UTC), sender_id=s.id)
    session.add(e)
    session.commit()
    session.refresh(e)

    rec = EmailReception(kind=RecipientKind.TO, email_id=e.id, contact_id=r.id)
    session.add(rec)
    session.commit()
    session.refresh(rec)

    assert rec.email_id == e.id and rec.contact_id == r.id
    assert rec.kind == RecipientKind.TO


def test_email_reception_composite_primary_key(session: Session):
    s = Contact(name="S", email_address="s@example.com")
    r = Contact(name="R", email_address="r@example.com")
    session.add_all([s, r])
    session.commit()

    e = Email(subject="Hello2", body="B", sent_at=datetime.now(UTC), sender_id=s.id)
    session.add(e)
    session.commit()
    session.refresh(e)

    rec1 = EmailReception(kind=RecipientKind.TO, email_id=e.id, contact_id=r.id)
    session.add(rec1)
    session.commit()

    # Expunge rec1 to avoid identity map conflict warning
    session.expunge(rec1)

    rec2 = EmailReception(kind=RecipientKind.CC, email_id=e.id, contact_id=r.id)
    session.add(rec2)

    with pytest.raises(IntegrityError):
        session.commit()


def test_email_reception_kind_variants(session: Session):
    s = Contact(name="S", email_address="s@example.com")
    r1 = Contact(name="R1", email_address="r1@example.com")
    r2 = Contact(name="R2", email_address="r2@example.com")
    r3 = Contact(name="R3", email_address="r3@example.com")
    session.add_all([s, r1, r2, r3])
    session.commit()

    e = Email(subject="Kinds", body="B", sent_at=datetime.now(UTC), sender_id=s.id)
    session.add(e)
    session.commit()
    session.refresh(e)

    session.add_all(
        [
            EmailReception(kind=RecipientKind.TO, email_id=e.id, contact_id=r1.id),
            EmailReception(kind=RecipientKind.CC, email_id=e.id, contact_id=r2.id),
            EmailReception(kind=RecipientKind.BCC, email_id=e.id, contact_id=r3.id),
        ]
    )
    session.commit()

    kinds = {rec.kind for rec in e.recipients}

    assert kinds == {RecipientKind.TO, RecipientKind.CC, RecipientKind.BCC}


def test_email_reception_relationships(session: Session):
    s = Contact(name="S", email_address="s@example.com")
    r = Contact(name="R", email_address="r@example.com")
    session.add_all([s, r])
    session.commit()

    e = Email(subject="Rel", body="B", sent_at=datetime.now(UTC), sender_id=s.id)
    session.add(e)
    session.commit()
    session.refresh(e)

    rec = EmailReception(kind=RecipientKind.TO, email_id=e.id, contact_id=r.id)
    session.add(rec)
    session.commit()
    session.refresh(rec)

    assert rec.email.subject == "Rel"
    assert rec.contact.email_address == "r@example.com"


def test_email_reception_multiple_recipients_query_by_kind(session: Session):
    s = Contact(name="S", email_address="s@example.com")
    r1 = Contact(name="R1", email_address="r1@example.com")
    r2 = Contact(name="R2", email_address="r2@example.com")
    session.add_all([s, r1, r2])
    session.commit()

    e = Email(subject="Q", body="B", sent_at=datetime.now(UTC), sender_id=s.id)
    session.add(e)
    session.commit()
    session.refresh(e)

    session.add_all(
        [
            EmailReception(kind=RecipientKind.TO, email_id=e.id, contact_id=r1.id),
            EmailReception(kind=RecipientKind.CC, email_id=e.id, contact_id=r2.id),
        ]
    )
    session.commit()

    tos = session.exec(select(EmailReception).where(EmailReception.kind == RecipientKind.TO)).all()

    assert len(tos) == 1 and tos[0].contact_id == r1.id
