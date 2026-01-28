# remail/scripts/seed_demo_data.py
"""
Seed demo data into SQLite DB for UI testing.

What it creates:
- A few Contacts
- A few Conversations
- One Thread per Conversation
- Multiple Emails per Thread (with realistic timestamps)
- Links:
  - UserConversation (user can see the conversation)
  - ConversationContact (participants)
  - EmailReception (recipient mapping)

Design goals:
- Deterministic enough for UI testing
- Safe to re-run (it cleans previous DEMO data first)
"""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from datetime import datetime, timedelta

from sqlalchemy import delete
from sqlmodel import Session, select

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


def _now() -> datetime:
    return datetime.now()


def _clean_demo_data(session: Session) -> None:
    """
    Remove previously seeded demo data.

    Strategy:
    - Emails: message_id startswith DEMO_MESSAGE_PREFIX OR subject contains DEMO_TAG
    - Threads: titles contain DEMO_TAG
    - Conversations: custom_name contains DEMO_TAG
    - Contacts: email_address endswith ".demo" OR name contains DEMO_TAG

    This keeps your fixtures / real data intact.
    """
    # Delete EmailReception rows linked to demo emails
    demo_email_ids = [
        e.id
        for e in session.exec(
            select(Email).where(
                (Email.message_id.startswith(DEMO_MESSAGE_PREFIX))  # type: ignore[attr-defined]
                | (Email.subject.contains(DEMO_TAG))  # type: ignore[attr-defined]
            )
        ).all()
        if e.id is not None
    ]
    if demo_email_ids:
        session.exec(delete(EmailReception).where(EmailReception.email_id.in_(demo_email_ids)))

    # Delete demo emails
    session.exec(
        delete(Email).where(
            (Email.message_id.startswith(DEMO_MESSAGE_PREFIX))  # type: ignore[attr-defined]
            | (Email.subject.contains(DEMO_TAG))  # type: ignore[attr-defined]
        )
    )

    # Delete demo threads
    demo_thread_ids = [
        t.id
        for t in session.exec(select(Thread).where(Thread.title.contains(DEMO_TAG))).all()  # type: ignore[attr-defined]
        if t.id is not None
    ]
    if demo_thread_ids:
        session.exec(delete(Thread).where(Thread.id.in_(demo_thread_ids)))

    # Delete demo user<->conversation links
    demo_conversation_ids = [
        c.id
        for c in session.exec(
            select(Conversation).where(Conversation.custom_name.contains(DEMO_TAG))  # type: ignore[attr-defined]
        ).all()
        if c.id is not None
    ]
    if demo_conversation_ids:
        session.exec(
            delete(UserConversation).where(
                UserConversation.conversation_id.in_(demo_conversation_ids)
            )
        )
        session.exec(
            delete(ConversationContact).where(
                ConversationContact.conversation_id.in_(demo_conversation_ids)
            )
        )
        session.exec(delete(Conversation).where(Conversation.id.in_(demo_conversation_ids)))

    # Delete demo contacts
    session.exec(
        delete(Contact).where(
            (Contact.email_address.endswith(".demo"))  # type: ignore[attr-defined]
            | (Contact.name.contains(DEMO_TAG))  # type: ignore[attr-defined]
        )
    )


def _ensure_user(session: Session, user_id: int | None = None) -> User:
    if user_id is None:
        user = session.exec(select(User).order_by(User.id.asc())).first()
        if not user:
            raise RuntimeError("No users found in DB. Run `pixi run init-db --fixtures` first.")
        return user

    user = session.exec(select(User).where(User.id == user_id)).first()
    if not user:
        raise RuntimeError(f"User id={user_id} not found.")
    return user


def _upsert_contact(session: Session, spec: DemoContactSpec) -> Contact:
    existing = session.exec(select(Contact).where(Contact.email_address == spec.email)).first()
    if existing:
        return existing

    c = Contact(
        name=spec.name,
        email_address=spec.email,
        is_known=True,
    )
    session.add(c)
    session.flush()  # assigns id
    return c


def _create_conversation_with_thread(
    session: Session,
    custom_name: str,
) -> tuple[Conversation, Thread]:
    conv = Conversation(custom_name=custom_name)
    session.add(conv)
    session.flush()

    th = Thread(title=f"{custom_name} {DEMO_TAG}", conversation_id=conv.id)
    session.add(th)
    session.flush()
    return conv, th


def _add_user_visibility(session: Session, user_id: int, conversation_id: int) -> None:
    link = session.exec(
        select(UserConversation).where(
            (UserConversation.user_id == user_id)
            & (UserConversation.conversation_id == conversation_id)
        )
    ).first()
    if link:
        return

    session.add(
        UserConversation(user_id=user_id, conversation_id=conversation_id, is_favorite=False)
    )


def _add_participant(session: Session, conversation_id: int, contact_id: int) -> None:
    link = session.exec(
        select(ConversationContact).where(
            (ConversationContact.conversation_id == conversation_id)
            & (ConversationContact.contact_id == contact_id)
        )
    ).first()
    if link:
        return

    session.add(ConversationContact(conversation_id=conversation_id, contact_id=contact_id))


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
) -> Email:
    e = Email(
        message_id=message_id,
        subject=subject,
        body=body,
        sent_at=sent_at,
        sender_id=sender_id,
        thread_id=thread_id,
    )
    session.add(e)
    session.flush()

    # recipient mapping (IN / TO, depending on your enum)
    # If your EmailReception.kind is an Enum, adjust accordingly.
    for rid in recipients:
        session.add(
            EmailReception(
                kind="TO",  # keep simple; change to your allowed values if needed
                email_id=e.id,  # type: ignore[arg-type]
                contact_id=rid,
            )
        )

    return e


def seed_demo_data(
    *, user_id: int | None = None, conversations: int = 3, emails_per_conversation: int = 5
) -> None:
    with Session(engine) as session:
        _clean_demo_data(session)

        user = _ensure_user(session, user_id=user_id)

        demo_contacts = [
            DemoContactSpec(name=f"Alice {DEMO_TAG}", email="alice@remail.demo"),
            DemoContactSpec(name=f"Bob {DEMO_TAG}", email="bob@remail.demo"),
            DemoContactSpec(name=f"Clara {DEMO_TAG}", email="clara@remail.demo"),
            DemoContactSpec(name=f"Newsletters {DEMO_TAG}", email="news@remail.demo"),
        ]
        contacts = [_upsert_contact(session, spec) for spec in demo_contacts]

        # Pick some senders
        senders = [contacts[0], contacts[1], contacts[2], contacts[3]]

        base = _now()

        for i in range(conversations):
            conv_name = f"Demo Conversation {i + 1} {DEMO_TAG}"
            conv, th = _create_conversation_with_thread(session, conv_name)

            _add_user_visibility(session, user.id, conv.id)  # type: ignore[arg-type]

            # add 2 participants to conversation
            p1 = contacts[i % len(contacts)]
            p2 = contacts[(i + 1) % len(contacts)]
            _add_participant(session, conv.id, p1.id)  # type: ignore[arg-type]
            _add_participant(session, conv.id, p2.id)  # type: ignore[arg-type]

            # generate emails
            for j in range(emails_per_conversation):
                sender = senders[(i + j) % len(senders)]
                sent_at = base - timedelta(hours=(i * 7 + j * 3), minutes=(j * 11))

                subject = f"{DEMO_TAG} Update {i + 1}-{j + 1}: UI test email"
                body = (
                    f"This is a seeded demo email for UI testing.\n\n"
                    f"Conversation: {conv_name}\n"
                    f"Thread id: {th.id}\n"
                    f"Sent at: {sent_at.isoformat(sep=' ', timespec='minutes')}\n"
                )
                msg_id = f"{DEMO_MESSAGE_PREFIX}{user.id}-{i + 1}-{j + 1}"

                # recipients: the two participants (excluding sender if desired)
                recips = [p1.id, p2.id]  # type: ignore[list-item]

                _add_email(
                    session,
                    thread_id=th.id,  # type: ignore[arg-type]
                    sender_id=sender.id,  # type: ignore[arg-type]
                    sent_at=sent_at,
                    subject=subject,
                    body=body,
                    recipients=recips,
                    message_id=msg_id,
                )

        session.commit()

        # quick summary
        email_count = len(session.exec(select(Email)).all())
        thread_count = len(session.exec(select(Thread)).all())
        conv_count = len(session.exec(select(Conversation)).all())
        print("✅ Seed done.")
        print(f"User: id={user.id} email={user.email}")
        print(f"Totals -> conversations={conv_count}, threads={thread_count}, emails={email_count}")


def main() -> None:
    # You can tweak these numbers for stress-testing UI lists.
    seed_demo_data(user_id=None, conversations=4, emails_per_conversation=6)


if __name__ == "__main__":
    main()
