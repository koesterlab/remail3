from email.message import EmailMessage
from pathlib import Path

import pytest

from remail.interfaces.email.services.message_builder import MessageBuilder


def test_build_message_sets_headers_and_body():
    msg = MessageBuilder.build_message(
        subject="Hello",
        body="Plain text body",
        from_addr="me@example.com",
        to=["a@x.com", "b@x.com"],
        cc=["c@x.com"],
    )

    assert isinstance(msg, EmailMessage)
    assert msg["Subject"] == "Hello"
    assert msg["From"] == "me@example.com"
    assert msg["To"] == "a@x.com, b@x.com"
    assert msg["Cc"] == "c@x.com"
    assert msg.get_content() == "Plain text body\n"


def test_build_message_skips_empty_to_and_cc():
    msg = MessageBuilder.build_message(
        subject="No recipients", body="Body", from_addr="me@example.com", to=[], cc=[]
    )

    assert msg["To"] is None
    assert msg["Cc"] is None
    assert msg["From"] == "me@example.com"
    assert msg["Subject"] == "No recipients"
    assert msg.get_content() == "Body\n"


def test_attach_files_adds_single_attachment(tmp_path: Path):
    text_file = tmp_path / "note.txt"
    text_file.write_text("hello world", encoding="utf-8")

    msg = MessageBuilder.build_message(
        subject="With attachment",
        body="See attached.",
        from_addr="me@example.com",
        to=["a@x.com"],
        cc=[],
    )

    MessageBuilder.attach_files(msg, [str(text_file)])
    body = msg.get_body(preferencelist=("plain",))
    attachments = list(msg.iter_attachments())
    att = attachments[0]

    assert msg.is_multipart()
    assert body is not None
    assert body.get_content() == "See attached.\n"
    assert len(attachments) == 1
    assert att.get_filename() == "note.txt"
    assert att.get_content_type() == "text/plain"
    assert att.get_payload(decode=True) == b"hello world"


def test_attach_files_multiple_and_unknown_mime(tmp_path: Path):
    txt = tmp_path / "a.txt"
    txt.write_text("a", encoding="utf-8")

    unknown = tmp_path / "blob.unknownext"
    unknown.write_bytes(b"\x00\x01\x02")

    msg = MessageBuilder.build_message(
        subject="Multi", body="Two files.", from_addr="me@example.com", to=["a@x.com"], cc=[]
    )

    MessageBuilder.attach_files(msg, [str(txt), str(unknown)])

    atts = list(msg.iter_attachments())

    assert [a.get_filename() for a in atts] == ["a.txt", "blob.unknownext"]
    assert atts[0].get_content_type() == "text/plain"
    assert atts[0].get_payload(decode=True) == b"a"
    assert atts[1].get_content_type() == "application/octet-stream"
    assert atts[1].get_payload(decode=True) == b"\x00\x01\x02"


def test_attach_files_raises_when_missing(tmp_path: Path):
    msg = MessageBuilder.build_message(
        subject="Missing", body="x", from_addr="me@example.com", to=["a@x.com"], cc=[]
    )

    missing = tmp_path / "nope.pdf"

    with pytest.raises(FileNotFoundError):
        MessageBuilder.attach_files(msg, [str(missing)])


def test_guess_mime_private_is_reasonable(tmp_path: Path):
    f = tmp_path / "file.whoknows"

    f.write_text("x", encoding="utf-8")

    main, sub = MessageBuilder._guess_mime(str(f))

    assert (main, sub) == ("application", "octet-stream")
