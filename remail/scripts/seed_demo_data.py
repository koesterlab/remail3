# remail/scripts/seed_demo_data.py


from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any, cast

from sqlalchemy import delete
from sqlmodel import Session, col, select

from remail.database.db import engine
from remail.models.contact import Contact
from remail.models.conversation import Conversation
from remail.models.conversation_contact import ConversationContact
from remail.models.email import Email
from remail.models.email_reception import EmailReception
from remail.models.thread import Thread
from remail.models.user import User
from remail.models.user_conversation import UserConversation

DEMO_TAG = "[DEMO]"
DEMO_MESSAGE_PREFIX = "demo-"  # used for message_id


@dataclass(frozen=True)
class DemoContactSpec:
    name: str
    email: str


def _require_id(value: int | None, *, what: str) -> int:
    if value is None:
        raise RuntimeError(f"Expected {what} to have an id, but it was None.")
    return value


def _now() -> datetime:
    return datetime.now()


def _clean_demo_data(session: Session) -> None:
    """
    Remove previously seeded demo data.
    """
    EmailAny = cast(Any, Email)
    subject_col = EmailAny.subject
    message_id_col = EmailAny.message_id

    demo_email_ids = [
        e.id
        for e in session.exec(
            select(Email).where(
                (col(message_id_col).startswith(DEMO_MESSAGE_PREFIX))
                | (col(subject_col).contains(DEMO_TAG))
            )
        ).all()
        if e.id is not None
    ]

    if demo_email_ids:
        session.exec(delete(EmailReception).where(col(EmailReception.email_id).in_(demo_email_ids)))

    session.exec(
        delete(Email).where(
            (col(message_id_col).startswith(DEMO_MESSAGE_PREFIX))
            | (col(subject_col).contains(DEMO_TAG))
        )
    )

    demo_thread_ids = [
        t.id
        for t in session.exec(select(Thread).where(col(Thread.title).contains(DEMO_TAG))).all()
        if t.id is not None
    ]

    if demo_thread_ids:
        session.exec(delete(Thread).where(col(Thread.id).in_(demo_thread_ids)))

    demo_conversation_ids = [
        c.id
        for c in session.exec(
            select(Conversation).where(col(Conversation.custom_name).contains(DEMO_TAG))
        ).all()
        if c.id is not None
    ]

    if demo_conversation_ids:
        session.exec(
            delete(UserConversation).where(
                col(UserConversation.conversation_id).in_(demo_conversation_ids)
            )
        )
        session.exec(
            delete(ConversationContact).where(
                col(ConversationContact.conversation_id).in_(demo_conversation_ids)
            )
        )
        session.exec(delete(Conversation).where(col(Conversation.id).in_(demo_conversation_ids)))

    session.exec(
        delete(Contact).where(
            (col(Contact.email_address).endswith(".demo")) | (col(Contact.name).contains(DEMO_TAG))
        )
    )


def _ensure_user(session: Session, user_id: int | None = None) -> User:
    if user_id is None:
        user = session.exec(select(User).order_by(col(User.id).asc())).first()
        if not user:
            raise RuntimeError("No users found in DB. Run `pixi run init-db --fixtures` first.")
        _require_id(user.id, what="user")
        return user

    user = session.exec(select(User).where(User.id == user_id)).first()
    if not user:
        raise RuntimeError(f"User id={user_id} not found.")
    _require_id(user.id, what="user")
    return user


def _upsert_contact(session: Session, spec: DemoContactSpec) -> Contact:
    existing = session.exec(select(Contact).where(Contact.email_address == spec.email)).first()
    if existing:
        _require_id(existing.id, what="contact")
        return existing

    c = Contact(
        name=spec.name,
        email_address=spec.email,
        is_known=True,
    )
    session.add(c)
    session.flush()
    _require_id(c.id, what="contact")
    return c


def _create_conversation_with_thread(
    session: Session,
    custom_name: str,
) -> tuple[Conversation, Thread]:
    conv = Conversation(custom_name=custom_name)
    session.add(conv)
    session.flush()
    conv_id = _require_id(conv.id, what="conversation")

    th = Thread(title=f"{custom_name} {DEMO_TAG}", conversation_id=conv_id)
    session.add(th)
    session.flush()
    _require_id(th.id, what="thread")

    return conv, th


def _add_user_visibility(session: Session, user_id: int, conversation_id: int) -> None:
    link = session.exec(
        select(UserConversation).where(
            (UserConversation.user_id == user_id)
            & (UserConversation.conversation_id == conversation_id)
        )
    ).first()
    if not link:
        session.add(
            UserConversation(
                user_id=user_id,
                conversation_id=conversation_id,
                is_favorite=False,
            )
        )


def _add_participant(session: Session, conversation_id: int, contact_id: int) -> None:
    link = session.exec(
        select(ConversationContact).where(
            (ConversationContact.conversation_id == conversation_id)
            & (ConversationContact.contact_id == contact_id)
        )
    ).first()
    if not link:
        session.add(
            ConversationContact(
                conversation_id=conversation_id,
                contact_id=contact_id,
            )
        )


def _add_email(
    session: Session,
    *,
    thread_id: int,
    sender_id: int,
    sent_at: datetime,
    subject: str,
    body: str,
    recipients: Iterable[int],
    message_id: str,
) -> None:
    email = Email(
        message_id=message_id,
        subject=subject,
        body=body,
        sent_at=sent_at,
        sender_id=sender_id,
        thread_id=thread_id,
    )
    session.add(email)
    session.flush()
    email_id = _require_id(email.id, what="email")

    for rid in recipients:
        session.add(
            EmailReception(
                kind="TO",
                email_id=email_id,
                contact_id=rid,
            )
        )


def seed_demo_data(
    *, user_id: int | None = None, conversations: int = 3, emails_per_conversation: int = 5
) -> None:
    with Session(engine) as session:
        _clean_demo_data(session)

        user = _ensure_user(session, user_id=user_id)
        user_id_int = _require_id(user.id, what="user")

        demo_contacts = [
            DemoContactSpec(name=f"Alice {DEMO_TAG}", email="alice@remail.demo"),
            DemoContactSpec(name=f"Bob {DEMO_TAG}", email="bob@remail.demo"),
            DemoContactSpec(name=f"Clara {DEMO_TAG}", email="clara@remail.demo"),
            DemoContactSpec(name=f"Newsletters {DEMO_TAG}", email="news@remail.demo"),
        ]
        contacts = [_upsert_contact(session, spec) for spec in demo_contacts]

        senders = contacts
        base = _now()

        for i in range(conversations):
            conv_name = f"Demo Conversation {i + 1} {DEMO_TAG}"
            conv, th = _create_conversation_with_thread(session, conv_name)
            conv_id = _require_id(conv.id, what="conversation")
            th_id = _require_id(th.id, what="thread")

            _add_user_visibility(session, user_id_int, conv_id)

            p1 = contacts[i % len(contacts)]
            p2 = contacts[(i + 1) % len(contacts)]
            p1_id = _require_id(p1.id, what="participant")
            p2_id = _require_id(p2.id, what="participant")

            _add_participant(session, conv_id, p1_id)
            _add_participant(session, conv_id, p2_id)

            for j in range(emails_per_conversation):
                sender = senders[(i + j) % len(senders)]
                sender_id = _require_id(sender.id, what="sender")

                sent_at = base - timedelta(hours=(i * 7 + j * 3), minutes=(j * 11))
                subject = f"{DEMO_TAG} Update {i + 1}-{j + 1}: UI test email"
                body = (
                    "This is a seeded demo email for UI testing.\n\n"
                    f"Conversation: {conv_name}\n"
                    f"Thread id: {th_id}\n"
                    f"Sent at: {sent_at.isoformat(sep=' ', timespec='minutes')}\n"
                )
                msg_id = f"{DEMO_MESSAGE_PREFIX}{user_id_int}-{i + 1}-{j + 1}"

                recipients = [rid for rid in (p1_id, p2_id) if rid != sender_id]

                _add_email(
                    session,
                    thread_id=th_id,
                    sender_id=sender_id,
                    sent_at=sent_at,
                    subject=subject,
                    body=body,
                    recipients=recipients,
                    message_id=msg_id,
                )

        session.commit()
        print("Seed demo data completed.")


def main() -> None:
    seed_demo_data(user_id=None, conversations=4, emails_per_conversation=6)


if __name__ == "__main__":
    main()
