from datetime import UTC, datetime, timedelta

import pytest
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, select

from remail.enums import Protocol
from remail.models import User


def test_user_create(session: Session):
    u = User(
        name="Ada",
        username="ada@example.com",
        email="ada@example.com",
        host="imap.example.com",
        password="secret",
        protocol=Protocol.IMAP,
    )
    session.add(u)
    session.commit()
    session.refresh(u)

    assert u.id is not None
    assert u.protocol == Protocol.IMAP
    assert u.host == "imap.example.com"


def test_user_auto_increment(session: Session):
    u1 = User(
        name="A",
        username="a@example.com",
        email="a@example.com",
        host="imap.example.com",
        password="x",
        protocol=Protocol.IMAP,
    )
    u2 = User(
        name="B",
        username="b@example.com",
        email="b@example.com",
        host="imap.example.com",
        password="x",
        protocol=Protocol.IMAP,
    )
    session.add(u1)
    session.add(u2)
    session.commit()
    session.refresh(u1)
    session.refresh(u2)

    assert u1.id is not None and u2.id is not None
    assert u2.id > u1.id


def test_user_unique_emails(session: Session):
    u1 = User(
        name="C",
        username="dup@example.com",
        email="dup@example.com",
        host="imap.example.com",
        password="x",
        protocol=Protocol.IMAP,
    )
    u2 = User(
        name="D",
        username="dup@example.com",
        email="dup@example.com",
        host="imap.example.com",
        password="y",
        protocol=Protocol.EXCHANGE,
    )
    session.add(u1)
    session.commit()
    session.add(u2)

    with pytest.raises(IntegrityError):
        session.commit()


def test_user_protocol_persistence(session: Session):
    u = User(
        name="Proto",
        username="p@example.com",
        email="p@example.com",
        host="imap.example.com",
        password="x",
        protocol=Protocol.IMAP,
    )
    session.add(u)
    session.commit()

    # switch protocol and persist
    u.protocol = Protocol.EXCHANGE
    session.add(u)
    session.commit()
    session.refresh(u)

    assert u.protocol == Protocol.EXCHANGE


def test_user_with_last_refresh(session: Session):
    now = datetime.now(UTC)
    u = User(
        name="Ref",
        username="ref@example.com",
        email="ref@example.com",
        host="imap.example.com",
        password="x",
        protocol=Protocol.IMAP,
        last_refresh=now,
    )
    session.add(u)
    session.commit()
    session.refresh(u)

    assert u.last_refresh == now.replace(tzinfo=None)


def test_user_update_last_refresh(session: Session):
    u = User(
        name="Upd",
        username="upd@example.com",
        email="upd@example.com",
        host="imap.example.com",
        password="x",
        protocol=Protocol.IMAP,
    )
    session.add(u)
    session.commit()
    session.refresh(u)

    new_time = datetime.now(UTC) + timedelta(minutes=5)
    u.last_refresh = new_time
    session.add(u)
    session.commit()
    session.refresh(u)

    assert u.last_refresh == new_time.replace(tzinfo=None)


def test_user_delete(session: Session):
    u = User(
        name="Del",
        username="del@example.com",
        email="del@example.com",
        host="imap.example.com",
        password="x",
        protocol=Protocol.IMAP,
    )
    session.add(u)
    session.commit()

    uid = u.id
    session.delete(u)
    session.commit()

    got = session.exec(select(User).where(User.id == uid)).first()

    assert got is None


def test_user_query_by_email(session: Session):
    u = User(
        name="Q",
        username="q@example.com",
        email="q@example.com",
        host="imap.example.com",
        password="x",
        protocol=Protocol.IMAP,
    )
    session.add(u)
    session.commit()

    got = session.exec(select(User).where(User.username == "q@example.com")).first()

    assert got is not None and got.name == "Q"


def test_user_query_by_protocol(session: Session):
    u1 = User(
        name="I",
        username="i@example.com",
        email="i@example.com",
        host="imap.example.com",
        password="x",
        protocol=Protocol.IMAP,
    )
    u2 = User(
        name="E",
        username="e@example.com",
        email="e@example.com",
        host="imap.example.com",
        password="x",
        protocol=Protocol.EXCHANGE,
    )
    session.add(u1)
    session.add(u2)
    session.commit()

    imap_user = session.exec(select(User).where(User.protocol == Protocol.IMAP)).first()

    assert imap_user and imap_user.username == "i@example.com"
