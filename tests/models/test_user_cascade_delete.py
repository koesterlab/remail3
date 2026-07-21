from datetime import UTC, datetime

from sqlmodel import Session, select

from remail.enums import Protocol
from remail.models import Contact, Conversation, Email, Thread, User


def _create_user(session: Session) -> User:
    user = User(name="testuser", email="test@example.com", protocol=Protocol.IMAP)
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


def test_user_cascade_delete_conversations(session: Session):
    user = _create_user(session)

    conversation = Conversation(custom_name="C", user_id=user.id)
    session.add(conversation)
    session.commit()
    conv_id = conversation.id

    session.delete(user)
    session.commit()

    assert session.exec(select(Conversation).where(Conversation.id == conv_id)).first() is None


def test_user_cascade_delete_chain(session: Session):
    user = _create_user(session)
    sender = Contact(name="S", email_address="s@example.com")

    conversation = Conversation(custom_name="C", user_id=user.id)
    session.add(sender)
    session.add(conversation)
    session.commit()

    thread = Thread(title="Subject", conversation_id=conversation.id)
    session.add(thread)
    session.commit()
    session.refresh(thread)

    e = Email(
        message_id="Chain",
        body="B",
        sent_at=datetime.now(UTC),
        sender_id=sender.id,
        thread_id=thread.id,
    )
    session.add(e)
    session.commit()
    conv_id, thread_id, email_id = conversation.id, thread.id, e.id

    session.delete(user)
    session.commit()

    assert session.exec(select(Conversation).where(Conversation.id == conv_id)).first() is None
    assert session.exec(select(Thread).where(Thread.id == thread_id)).first() is None
    assert session.exec(select(Email).where(Email.id == email_id)).first() is None
