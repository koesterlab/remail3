from datetime import datetime

from sqlmodel import select

from remail.interfaces.email.services.tag_service import DEFAULT_TAGS, TagService
from remail.models import Contact, Email, EmailTag, Tag


def _add_email(session, thread_id: int) -> Email:
    contact = Contact(name="Sender", email_address="sender@example.com")
    session.add(contact)
    session.flush()
    email = Email(
        body="body",
        sent_at=datetime.now(),
        sender_id=contact.id,
        thread_id=thread_id,
    )
    session.add(email)
    session.flush()
    return email


def test_seed_default_tags_populates_empty_table(session):
    service = TagService()

    service.seed_default_tags(session=session)
    tags = service.get_all_tags(session=session)

    assert {tag.name for tag in tags} == {name for name, _description in DEFAULT_TAGS}

    service.delete_tag(tags[0].id, session=session)
    service.seed_default_tags(session=session)

    assert len(service.get_all_tags(session=session)) == len(DEFAULT_TAGS) - 1


def test_create_and_delete_tag(session):
    service = TagService()

    tag = service.create_tag("Project", "Project emails", session=session)

    assert tag.name == "Project"
    assert any(saved.name == "Project" for saved in service.get_all_tags(session=session))

    service.delete_tag(tag.id, session=session)

    assert all(saved.name != "Project" for saved in service.get_all_tags(session=session))


def test_get_thread_tags_returns_union_of_email_tags(session):
    service = TagService()
    work = service.create_tag("Work", session=session)
    finance = service.create_tag("Finance", session=session)
    urgent = service.create_tag("Urgent", session=session)

    first = _add_email(session, thread_id=1)
    second = _add_email(session, thread_id=1)
    other_thread = _add_email(session, thread_id=2)
    session.add(EmailTag(tag_id=work.id, email_id=first.id))
    session.add(EmailTag(tag_id=finance.id, email_id=second.id))
    session.add(EmailTag(tag_id=urgent.id, email_id=other_thread.id))

    assert {tag.name for tag in service.get_thread_tags(1, session=session)} == {
        "Work",
        "Finance",
    }
    assert {tag.name for tag in service.get_thread_tags(2, session=session)} == {"Urgent"}
    assert service.get_thread_tags(99, session=session) == []


def test_set_email_tags_replaces_assignments(session):
    service = TagService()
    service.create_tag("Work", session=session)
    service.create_tag("Finance", session=session)
    email = _add_email(session, thread_id=1)

    service.set_email_tags(email.id, ["Work"], session=session)
    assert {tag.name for tag in service.get_thread_tags(1, session=session)} == {"Work"}

    service.set_email_tags(email.id, ["Finance", "Unknown"], session=session)
    assert {tag.name for tag in service.get_thread_tags(1, session=session)} == {"Finance"}

    service.set_email_tags(email.id, [], session=session)
    assert service.get_thread_tags(1, session=session) == []


def test_get_tags_for_email_scores_best_chunk(session):
    service = TagService()
    # Pre-populate the embedding and baseline caches so no embedding model is
    # needed; zero baselines make calibrated scores equal the raw similarities.
    service._tag_embedding_cache["Work"] = [1.0, 0.0]
    service._tag_embedding_cache["Finance"] = [0.0, 1.0]
    service._tag_baseline_cache = {"Work": 0.0, "Finance": 0.0}
    tags = [Tag(name="Work"), Tag(name="Finance")]

    # First chunk matches Work, second matches Finance; the scores are nearly
    # tied, so the margin rule assigns both.
    chunk_vectors = [[0.9, 0.1], [0.05, 0.8]]
    assert set(service.get_tags_for_email(chunk_vectors, tags)) == {"Work", "Finance"}

    # A clearly weaker tag is not dragged in by the margin rule.
    assert service.get_tags_for_email([[1.0, 0.0]], tags) == ["Work"]

    # A chunk orthogonal to the only tag scores 0 and stays below the floor.
    assert service.get_tags_for_email([[1.0, 0.0]], [Tag(name="Finance")]) == []

    assert service.get_tags_for_email([], tags) == []


def test_delete_tag_removes_email_tag_links(session):
    service = TagService()
    tag = service.create_tag("Project", session=session)
    email = _add_email(session, thread_id=1)
    session.add(EmailTag(tag_id=tag.id, email_id=email.id))
    session.flush()

    service.delete_tag(tag.id, session=session)

    assert session.exec(select(EmailTag).where(EmailTag.tag_id == tag.id)).all() == []
    assert service.get_thread_tags(1, session=session) == []
