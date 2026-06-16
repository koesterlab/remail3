from datetime import UTC, datetime

from sqlmodel import Session, select

from remail.interfaces.email.services.tag_service import DEFAULT_TAGS, TagService
from remail.models import Contact, Email, EmailTag, Thread


def _create_email_thread(session: Session) -> Thread:
    sender = Contact(name="Sender", email_address="sender@example.com")
    thread = Thread(title="Taggable thread", conversation_id=1)
    session.add(sender)
    session.add(thread)
    session.commit()
    session.refresh(sender)
    session.refresh(thread)

    email = Email(
        message_id="tag-test",
        body="Please tag this email.",
        sent_at=datetime.now(UTC),
        sender_id=sender.id,
        thread_id=thread.id,
    )
    session.add(email)
    session.commit()
    session.refresh(thread)
    return thread


def test_get_all_tags_seeds_defaults(session: Session):
    service = TagService()

    tags = service.get_all_tags(session=session)

    assert {tag.name for tag in tags} == {name for name, _ in DEFAULT_TAGS}


def test_create_and_delete_tag(session: Session):
    service = TagService()

    tag = service.create_tag("Study", "University messages", session=session)
    assert tag.id is not None
    assert tag.name == "Study"

    service.delete_tag(tag.id, session=session)

    names = {existing_tag.name for existing_tag in service.get_all_tags(session=session)}
    assert "Study" not in names


def test_add_and_remove_tag_from_thread(session: Session):
    thread = _create_email_thread(session)
    service = TagService()
    tag = service.create_tag("Project", "Project work", session=session)

    service.add_tag_to_thread(thread.id, tag.id, session=session)
    tags = service.get_tags_for_thread(thread.id, session=session)

    assert [thread_tag.name for thread_tag in tags] == ["Project"]

    service.remove_tag_from_thread(thread.id, tag.id, session=session)
    assert service.get_tags_for_thread(thread.id, session=session) == []
    assert session.exec(select(EmailTag).where(EmailTag.tag_id == tag.id)).first() is None
