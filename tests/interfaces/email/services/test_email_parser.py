from datetime import UTC, datetime
from email.message import EmailMessage
from email.utils import format_datetime

import pytest

import remail.interfaces.email.services.email_parser as email_parser_mod
from remail.interfaces.email.services.email_parser import EmailParser


@pytest.fixture(autouse=True)
def patch_save_attachment(monkeypatch):
    """Replace save_attachment so tests don't touch the filesystem."""

    def fake_save_attachment(filename, payload, message_id):
        assert isinstance(payload, (bytes, bytearray))
        return f"/stored/{filename}"

    monkeypatch.setattr(email_parser_mod, "save_attachment", fake_save_attachment, raising=True)


@pytest.fixture
def test_user(test_engine):
    """Create a test user in the database."""
    from sqlmodel import Session

    from remail.enums import Protocol
    from remail.models import User

    with Session(test_engine) as session:
        user = User(
            name="test",
            email="test@example.com",
            protocol=Protocol.IMAP,
            connection='{"host": "imap.example.com"}',
        )
        session.add(user)
        session.commit()
        session.refresh(user)
        return user.id


@pytest.fixture
def parser(test_user) -> EmailParser:
    return EmailParser(user_id=test_user)


def test_extract_msg_date_happy_path(parser: EmailParser):
    msg = EmailMessage()
    dt = datetime(2025, 1, 2, 15, 30, tzinfo=UTC)
    msg["Date"] = format_datetime(dt)
    got = parser.extract_msg_date(msg)

    assert got is not None
    assert got.tzinfo is None
    assert got == dt.replace(tzinfo=None)


def test_extract_msg_date_missing_or_bad(parser: EmailParser):
    msg = EmailMessage()
    msg2 = EmailMessage()
    msg2["Date"] = "not-a-real-date"

    assert parser.extract_msg_date(msg) is None
    assert parser.extract_msg_date(msg2) is None


def test_get_body_multipart_plain_html_and_attachment(parser: EmailParser):
    msg = EmailMessage()
    msg["Message-Id"] = "<msg-123@example.com>"
    msg.set_content("Hello plain body")
    msg.add_alternative("<p>Hello <b>HTML</b></p>", subtype="html")
    msg.add_attachment(
        b"\x01\x02", maintype="application", subtype="octet-stream", filename="file.bin"
    )

    body = parser._get_body(msg)

    assert body == "Hello plain body\n"


def test_get_body_html_only(parser: EmailParser):
    msg = EmailMessage()
    msg.set_content("<h1>Hi</h1>", subtype="html")

    body = parser._get_body(msg)

    assert body == ""


def test_get_body_plain_only(parser: EmailParser):
    msg = EmailMessage()
    msg.set_content("Just text.")

    body = parser._get_body(msg)

    assert body == "Just text.\n"


def test_get_body_skips_empty_attachment_payload(parser: EmailParser):
    msg = EmailMessage()
    msg.set_content("body")
    msg.add_attachment(b"", maintype="application", subtype="octet-stream", filename="empty.bin")

    body = parser._get_body(msg)

    assert body == "body\n"


def test_strip_reply_history_on_wrote(parser: EmailParser):
    body = (
        "Here is my short reply.\n\n"
        "On Tue, Jul 2, 2026 at 10:00 AM Alice <alice@example.com> wrote:\n"
        "> Previous line\n"
    )

    assert parser._strip_reply_history(body) == "Here is my short reply."


def test_strip_reply_history_german_marker(parser: EmailParser):
    body = (
        "Danke fur die Infos.\n\n"
        "Am 02.07.2026 um 09:10 schrieb Max Mustermann <max@example.com>:\n"
        "> Alter Verlauf\n"
    )

    assert parser._strip_reply_history(body) == "Danke fur die Infos."


def test_strip_reply_history_preserves_plain_message(parser: EmailParser):
    body = "Nur eine normale Nachricht ohne Verlauf."

    assert parser._strip_reply_history(body) == body
