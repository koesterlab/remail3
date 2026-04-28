from datetime import datetime, timedelta
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest

import remail.interfaces.email.protocols.imap as proto_mod
from remail import errors as ee
from remail.interfaces.email.protocols.imap import ImapProtocol


@pytest.fixture
def imap_mock():
    return MagicMock(spec=proto_mod.IMAPClient)


@pytest.fixture
def folder_service_mock(imap_mock, monkeypatch):
    fs = MagicMock(spec=proto_mod.FolderService)

    fs.get_all_folders.return_value = ["INBOX", "Work"]

    class DummyCtx:
        def __init__(self, *a, **k):
            pass

        def __enter__(self):
            return None

        def __exit__(self, exc_type, exc, tb):
            return False

    fs.selected_folder.side_effect = lambda name: DummyCtx()

    monkeypatch.setattr(
        proto_mod.FolderService,
        "build_search_criteria",
        staticmethod(
            lambda since, flags: (
                (["SINCE", since.date()] if since else []) + (flags or []) or ["ALL"]
            )
        ),
    )

    return fs


@pytest.fixture
def email_parser_mock(monkeypatch):
    ep = MagicMock(spec=proto_mod.EmailParser)
    ep.extract_msg_date.side_effect = lambda em: getattr(em, "dt", None)

    return ep


@pytest.fixture
def smtp_sender_mock():
    s = MagicMock(spec=proto_mod.SmtpSender)

    return s


@pytest.fixture
def protocol(imap_mock, folder_service_mock, email_parser_mock, smtp_sender_mock, monkeypatch):
    monkeypatch.setattr(proto_mod, "IMAPClient", MagicMock(return_value=imap_mock))
    monkeypatch.setattr(proto_mod, "FolderService", MagicMock(return_value=folder_service_mock))
    monkeypatch.setattr(proto_mod, "EmailParser", MagicMock(return_value=email_parser_mock))
    monkeypatch.setattr(proto_mod, "SmtpSender", MagicMock(return_value=smtp_sender_mock))

    p = ImapProtocol(username="user@example.com", password="pw", host="imap.example.com")

    return p


def test_login_success(protocol: ImapProtocol, imap_mock):
    assert not protocol.logged_in

    protocol.login()
    imap_mock.login.assert_called_once_with("user@example.com", "pw")

    assert protocol.logged_in is True


def test_login_rejects_missing_creds(protocol: ImapProtocol):
    protocol.user_username = None
    protocol.user_password = None

    with pytest.raises(ee.InvalidLoginData):
        protocol.login()


def test_login_maps_loginerror(protocol: ImapProtocol, imap_mock):
    imap_mock.login.side_effect = proto_mod.LoginError("bad creds")

    with pytest.raises(ee.InvalidLoginData):
        protocol.login()


class FakeMsg:
    """Minimal object to simulate parsed message objects used by parser."""

    def __init__(self, id, dt=None):
        self.id = id
        self.dt = dt


def test_fetch_emails_across_folders_and_filter_by_since(
    protocol: ImapProtocol, imap_mock, folder_service_mock, email_parser_mock, monkeypatch
):
    imap_mock.search.side_effect = [
        [1, 2],
        [],
    ]

    now = datetime.now()
    earlier = now - timedelta(hours=2)
    later = now + timedelta(hours=2)

    imap_mock.fetch.side_effect = [{1: {b"RFC822": b"A"}, 2: {b"RFC822": b"B"}}]

    msgs = [FakeMsg("A", earlier), FakeMsg("B", later)]
    monkeypatch.setattr(proto_mod.py_email, "message_from_bytes", MagicMock(side_effect=msgs))

    protocol._logged_in = True
    out = protocol.fetch_emails(folder=None, since=now, flags=["UNSEEN"])

    imap_mock.fetch.assert_called_once()

    assert imap_mock.search.call_count == 2
    assert out == [(2, msgs[1])]


def test_fetch_emails_specific_folder(
    protocol: ImapProtocol, imap_mock, folder_service_mock, monkeypatch
):
    imap_mock.search.return_value = [10]
    imap_mock.fetch.return_value = {10: {b"RFC822": b"M"}}

    msg = FakeMsg("M", None)
    monkeypatch.setattr(proto_mod.py_email, "message_from_bytes", MagicMock(side_effect=[msg]))

    protocol._logged_in = True
    out = protocol.fetch_emails(folder="INBOX", since=None, flags=None)

    folder_service_mock.selected_folder.assert_called_once_with("INBOX")
    assert out == [(10, msg)]


def test_fetch_emails_requires_login(protocol: ImapProtocol):
    protocol._logged_in = False

    with pytest.raises(ee.NotLoggedIn):
        protocol.fetch_emails()


class DummyAttachment:
    def __init__(self, filename):
        self.filename = filename


class DummyEmail:
    def __init__(self, subject, body, recipients, attachments=None):
        self.subject = subject
        self.body = body
        self.recipients = recipients
        self.attachments = attachments or []


def test_send_email_happy_path(protocol: ImapProtocol, smtp_sender_mock, monkeypatch):
    protocol._logged_in = True

    with (
        patch.object(
            proto_mod.MessageBuilder, "build_message", return_value=SimpleNamespace(msg=True)
        ) as build_mock,
        patch.object(proto_mod.MessageBuilder, "attach_files") as attach_mock,
    ):
        contact = SimpleNamespace(first_name="A", last_name="One", email_address="a@x.com")
        conversation = SimpleNamespace(contacts=[contact])
        thread = SimpleNamespace(title="S", conversation=conversation)
        mail = SimpleNamespace(
            thread=thread,
            body="B",
            attachments=[DummyAttachment("f1.txt"), DummyAttachment("f2.pdf")],
        )

        protocol.send_email(mail)
        smtp_sender_mock.validate_send_state.assert_called_once_with(True)
        build_mock.assert_called_once_with(
            subject="S", body="B", from_addr="user@example.com", to=["A One <a@x.com>"], cc=[]
        )
        attach_mock.assert_called_once()
        smtp_sender_mock.send.assert_called_once_with(SimpleNamespace(msg=True), ["a@x.com"])


def test_send_email_no_recipients_sends_empty_envelope(protocol: ImapProtocol, smtp_sender_mock):
    protocol._logged_in = True

    with patch.object(
        proto_mod.MessageBuilder, "build_message", return_value=SimpleNamespace(msg=True)
    ):
        conversation = SimpleNamespace(contacts=[])
        thread = SimpleNamespace(title="S", conversation=conversation)
        mail = SimpleNamespace(thread=thread, body="B", attachments=[])
        protocol.send_email(mail)

    smtp_sender_mock.validate_send_state.assert_called_once_with(True)
    assert smtp_sender_mock.send.call_count == 1
    assert smtp_sender_mock.send.call_args[0][1] == []
