from datetime import datetime, timedelta

from sqlmodel import Session

from remail.client.views.settings.attachments_view import (
    AttachmentGroup,
    AttachmentsView,
    AttachmentVersion,
)
from remail.models import Attachment, Contact, Conversation, Email, Thread
from remail.utils.file_opener import open_file


def test_load_attachment_groups_groups_versions_by_thread_and_filename(session: Session):
    contact = Contact(name="Alice Sender", email_address="alice@example.com")
    conversation = Conversation(custom_name="Project")
    session.add(contact)
    session.add(conversation)
    session.commit()

    thread = Thread(title="Budget", conversation_id=conversation.id)
    session.add(thread)
    session.commit()

    older = Email(
        message_id="older",
        body="old",
        sent_at=datetime(2026, 1, 1),
        sender_id=contact.id,
        thread_id=thread.id,
    )
    newer = Email(
        message_id="newer",
        body="new",
        sent_at=older.sent_at + timedelta(days=1),
        sender_id=contact.id,
        thread_id=thread.id,
    )
    session.add(older)
    session.add(newer)
    session.commit()

    session.add(Attachment(filename="offer.pdf", email_id=older.id))
    session.add(Attachment(filename="Offer.pdf", email_id=newer.id))
    session.commit()

    view = object.__new__(AttachmentsView)
    groups = AttachmentsView._load_attachment_groups(view, session=session)

    assert len(groups) == 1
    assert groups[0].filename == "offer.pdf"
    assert groups[0].thread_title == "Budget"
    assert [version.sent_at for version in groups[0].versions] == [newer.sent_at, older.sent_at]
    assert groups[0].sender_email == "alice@example.com"


def test_load_attachment_groups_keeps_same_filename_separate_across_threads(session: Session):
    contact = Contact(name="Alice Sender", email_address="alice@example.com")
    conversation = Conversation(custom_name="Project")
    session.add(contact)
    session.add(conversation)
    session.commit()

    budget_thread = Thread(title="Budget", conversation_id=conversation.id)
    invoice_thread = Thread(title="Invoice", conversation_id=conversation.id)
    session.add(budget_thread)
    session.add(invoice_thread)
    session.commit()

    budget_email = Email(
        message_id="budget",
        body="budget",
        sent_at=datetime(2026, 1, 1),
        sender_id=contact.id,
        thread_id=budget_thread.id,
    )
    invoice_email = Email(
        message_id="invoice",
        body="invoice",
        sent_at=datetime(2026, 1, 2),
        sender_id=contact.id,
        thread_id=invoice_thread.id,
    )
    session.add(budget_email)
    session.add(invoice_email)
    session.commit()

    session.add(Attachment(filename="offer.pdf", email_id=budget_email.id))
    session.add(Attachment(filename="offer.pdf", email_id=invoice_email.id))
    session.commit()

    view = object.__new__(AttachmentsView)
    groups = AttachmentsView._load_attachment_groups(view, session=session)

    assert len(groups) == 2
    assert {group.thread_title for group in groups} == {"Budget", "Invoice"}
    assert [group.thread_title for group in groups] == ["Invoice", "Budget"]
    assert all(len(group.versions) == 1 for group in groups)


def test_attachment_group_prepares_search_text():
    group = AttachmentGroup(
        filename="Offer.pdf",
        thread_title="Budget",
        sender_name="Alice Sender",
        sender_email="alice@example.com",
        versions=[
            AttachmentVersion(
                filename="Offer.pdf",
                sender_name="Alice Sender",
                sender_email="alice@example.com",
                thread_title="Budget",
                sent_at=datetime(2026, 1, 1),
                file_path="",
                file_size=0,
                file_type="application/pdf",
            )
        ],
    )

    search_text = AttachmentsView._attachment_search_text(group)

    assert "offer.pdf" in search_text
    assert "alice@example.com" in search_text
    assert "application/pdf" in search_text


def test_open_attachment_file_returns_false_for_missing_path():
    assert AttachmentsView._open_attachment_file("missing-file-that-should-not-exist.pdf") is False
