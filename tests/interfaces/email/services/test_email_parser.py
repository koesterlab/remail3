from datetime import UTC, datetime
from email.message import EmailMessage
from email.utils import format_datetime

import pytest

import remail.interfaces.email.services.email_parser as email_parser_mod
from remail.interfaces.email.services.email_parser import EmailParser


class FakeEmail:
    def __init__(self, message_id, sender, subject, body, recipients, date):
        self.message_id = message_id
        self.sender = sender
        self.subject = subject
        self.body = body
        self.recipients = recipients
        self.date = date
        self.attachments = []


class FakeAttachment:
    def __init__(self, filename, email):
        self.filename = filename
        self.email = email


@pytest.fixture(autouse=True)
def patch_models_and_helpers(monkeypatch):
    """
    Replace Email, Attachment, and save_attachment in the module under test
    so we don't need the real DB models or filesystem writes.
    """

    monkeypatch.setattr(email_parser_mod, "Email", FakeEmail, raising=True)
    monkeypatch.setattr(email_parser_mod, "Attachment", FakeAttachment, raising=True)

    def fake_save_attachment(filename, payload, message_id):
        assert isinstance(payload, (bytes, bytearray))

        return f"/stored/{filename}"

    monkeypatch.setattr(email_parser_mod, "save_attachment", fake_save_attachment, raising=True)


@pytest.fixture
def parser() -> EmailParser:
    return EmailParser()


def test_safe_msg_datetime_happy_path(parser: EmailParser):
    msg = EmailMessage()
    dt = datetime(2025, 1, 2, 15, 30, tzinfo=UTC)
    msg["Date"] = format_datetime(dt)
    got = parser.safe_msg_datetime(msg)

    assert got is not None
    assert got.tzinfo is not None
    assert got == dt


def test_safe_msg_datetime_missing_or_bad(parser: EmailParser):
    msg = EmailMessage()
    msg2 = EmailMessage()
    msg2["Date"] = "not-a-real-date"

    assert parser.safe_msg_datetime(msg) is None
    assert parser.safe_msg_datetime(msg2) is None


def test_decode_header_plain_and_encoded(parser: EmailParser):
    encoded = "=?utf-8?b?R3LDvMOfZQ==?="

    assert parser.decode_header(None) == ""
    assert parser.decode_header("Hello") == "Hello"
    assert parser.decode_header(encoded) == "Grüße"


def test_parse_email_message_multipart_plain_html_and_attachment(parser: EmailParser):
    msg = EmailMessage()
    msg["Subject"] = "=?utf-8?b?VGVzdCDigJxTdWJqZWN04oCd?="
    msg["From"] = "Alice <alice@example.com>"
    msg["To"] = "Bob <bob@example.com>"
    msg["Message-Id"] = "<msg-123@example.com>"
    msg["Date"] = format_datetime(datetime(2025, 1, 2, 12, 0, tzinfo=UTC))

    msg.set_content("Hello plain body")
    msg.add_alternative("<p>Hello <b>HTML</b></p>", subtype="html")
    msg.add_attachment(
        b"\x01\x02", maintype="application", subtype="octet-stream", filename="file.bin"
    )

    email_obj = parser.parse_email_message(msg)
    att = email_obj.attachments[0]

    assert isinstance(email_obj, FakeEmail)
    assert email_obj.message_id == "<msg-123@example.com>"
    assert email_obj.subject == "Test “Subject”"
    assert email_obj.body == "Hello plain body\n"
    assert email_obj.recipients == []
    assert email_obj.sender is None
    assert email_obj.date is not None
    assert len(email_obj.attachments) == 1
    assert isinstance(att, FakeAttachment)
    assert att.filename == "/stored/file.bin"
    assert att.email is email_obj


def test_parse_email_message_html_only(parser: EmailParser):
    msg = EmailMessage()
    msg["Subject"] = "HTML only"
    msg["Message-Id"] = "<id-2@example.com>"

    msg.set_content("<h1>Hi</h1>", subtype="html")

    email_obj = parser.parse_email_message(msg)

    assert email_obj.body == ""
    assert email_obj.subject == "HTML only"
    assert email_obj.attachments == []


def test_parse_email_message_plain_only(parser: EmailParser):
    msg = EmailMessage()
    msg["Subject"] = "Plain only"
    msg["Message-Id"] = "<id-3@example.com>"
    msg.set_content("Just text.")

    email_obj = parser.parse_email_message(msg)

    assert email_obj.body == "Just text.\n"
    assert email_obj.attachments == []


def test_parse_email_message_skips_empty_attachment_payload(parser: EmailParser):
    msg = EmailMessage()
    msg["Subject"] = "Empty attachment"
    msg["Message-Id"] = "<id-4@example.com>"
    msg.set_content("body")

    msg.add_attachment(b"", maintype="application", subtype="octet-stream", filename="empty.bin")

    email_obj = parser.parse_email_message(msg)

    assert email_obj.attachments == []
