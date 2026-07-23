from datetime import UTC, datetime

from sqlmodel import Session

from remail.controllers.dtos.threads import ThreadDTO  # noqa: F401
from remail.enums import Protocol
from remail.interfaces.email.services.thread_service import ThreadService
from remail.models import Contact, Conversation, Email, EmailTag, Tag, Thread, User


def _add_user(session: Session, email: str) -> User:
    user = User(
        name="Test User",
        email=email,
        protocol=Protocol.IMAP,
        connection="{}",
    )
    session.add(user)
    session.flush()
    return user


def _add_tag(session: Session, name: str) -> Tag:
    tag = Tag(name=name, description="")
    session.add(tag)
    session.flush()
    return tag


def _add_thread(
    session: Session,
    user: User,
    title: str,
    last_message_time: datetime,
) -> Thread:
    conversation = Conversation(user_id=user.id)
    session.add(conversation)
    session.flush()

    thread = Thread(
        title=title,
        conversation_id=conversation.id,
        last_message_time=last_message_time,
    )
    session.add(thread)
    session.flush()
    return thread


def _add_email(
    session: Session,
    thread: Thread,
    sender_email: str,
    tag_ids: list[int] | None = None,
) -> Email:
    contact = Contact(email_address=sender_email, name="Sender Name")
    session.add(contact)
    session.flush()

    email = Email(
        message_id=f"test-message-{thread.id}-{sender_email}",
        body="This is a test email.",
        sender_id=contact.id,
        thread_id=thread.id,
        sent_at=datetime.now(UTC),
    )
    session.add(email)
    session.flush()

    if tag_ids:
        for tag_id in tag_ids:
            email_tag = EmailTag(email_id=email.id, tag_id=tag_id)
            session.add(email_tag)

    session.flush()
    return email


def test_filters_threads_by_tag_and_returns_each_thread_once(
    session: Session,
) -> None:
    user = _add_user(session, "user@example.com")
    work_tag = _add_tag(session, "Work")
    personal_tag = _add_tag(session, "Personal")
    assert work_tag.id is not None
    assert personal_tag.id is not None

    newest_personal = _add_thread(
        session,
        user,
        "Newest Personal",
        datetime(2024, 1, 3),
    )
    newer_work = _add_thread(
        session,
        user,
        "Newer Work",
        datetime(2024, 1, 2),
    )
    older_work = _add_thread(
        session,
        user,
        "Older Work",
        datetime(2024, 1, 1),
    )

    _add_email(
        session,
        newest_personal,
        "personal@example.com",
        [personal_tag.id],
    )
    _add_email(
        session,
        newer_work,
        "work-one@example.com",
        [work_tag.id],
    )
    _add_email(
        session,
        newer_work,
        "work-two@example.com",
        [work_tag.id],
    )
    _add_email(
        session,
        older_work,
        "work-three@example.com",
        [work_tag.id],
    )
    session.commit()

    results = ThreadService().get_most_important_threads(
        count=5,
        tag_id=work_tag.id,
        session=session,
    )

    titles = [thread.title for thread, _conversation, _user in results]

    assert titles == ["Newer Work", "Older Work"]


def test_filters_by_tag_before_applying_count_limit(session: Session) -> None:
    user = _add_user(session, "limit-user@example.com")
    work_tag = _add_tag(session, "Limit Work")
    personal_tag = _add_tag(session, "Limit Personal")
    assert work_tag.id is not None
    assert personal_tag.id is not None

    newest_personal = _add_thread(
        session,
        user,
        "Newest Non-Match",
        datetime(2024, 2, 2),
    )
    older_work = _add_thread(
        session,
        user,
        "Older Match",
        datetime(2024, 2, 1),
    )

    _add_email(
        session,
        newest_personal,
        "limit-personal@example.com",
        [personal_tag.id],
    )
    _add_email(
        session,
        older_work,
        "limit-work@example.com",
        [work_tag.id],
    )
    session.commit()

    results = ThreadService().get_most_important_threads(
        count=1,
        tag_id=work_tag.id,
        session=session,
    )

    assert [thread.title for thread, _conversation, _user in results] == ["Older Match"]


def test_skips_threads_whose_conversation_has_no_user(session: Session) -> None:
    orphan_conversation = Conversation(user_id=None)
    session.add(orphan_conversation)
    session.flush()

    orphan_thread = Thread(
        title="Orphan Thread",
        conversation_id=orphan_conversation.id,
        last_message_time=datetime(2024, 3, 1),
    )
    session.add(orphan_thread)
    session.commit()

    results = ThreadService().get_most_important_threads(
        count=5,
        session=session,
    )

    assert results == []
