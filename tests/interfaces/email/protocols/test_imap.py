from datetime import UTC, datetime
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

    fs.get_user_folders.return_value = ["INBOX", "Work"]

    class DummyCtx:
        def __init__(self, *a, **k):
            pass

        def __enter__(self):
            return None

        def __exit__(self, exc_type, exc, tb):
            return False

    fs.selected_folder.side_effect = lambda name: DummyCtx()
    fs.get_trash_folder.return_value = "Trash"

    monkeypatch.setattr(
        proto_mod.FolderService,
        "build_search_criteria",
        staticmethod(
            lambda since, flags: (["SINCE", since.date()] if since else []) + (flags or [])
            or ["ALL"]
        ),
    )

    return fs


@pytest.fixture
def email_parser_mock(monkeypatch):
    ep = MagicMock(spec=proto_mod.EmailParser)
    ep.parse_email_message.side_effect = lambda em: f"parsed:{getattr(em, 'id', 'msg')}"

    monkeypatch.setattr(
        proto_mod.EmailParser, "safe_msg_datetime", staticmethod(lambda em: getattr(em, "dt", None))
    )

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


def test_logout_resets_state(protocol: ImapProtocol, imap_mock, smtp_sender_mock):
    protocol._logged_in = True

    protocol.logout()
    imap_mock.logout.assert_called_once()

    assert protocol.user_username is None
    assert protocol.user_password is None
    assert smtp_sender_mock.username is None
    assert smtp_sender_mock.password is None
    assert protocol.logged_in is False


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

    now = datetime(2025, 1, 2, 13, 0, tzinfo=UTC)
    earlier = datetime(2025, 1, 2, 11, 0, tzinfo=UTC)
    later = datetime(2025, 1, 2, 15, 0, tzinfo=UTC)

    imap_mock.fetch.side_effect = [{1: {b"RFC822": b"A"}, 2: {b"RFC822": b"B"}}]

    msgs = [FakeMsg("A", earlier), FakeMsg("B", later)]
    monkeypatch.setattr(proto_mod.py_email, "message_from_bytes", MagicMock(side_effect=msgs))

    protocol._logged_in = True
    out = protocol.fetch_emails(folder=None, since=now, flags=["UNSEEN"])

    imap_mock.fetch.assert_called_once()

    assert imap_mock.search.call_count == 2
    assert out == ["parsed:B"]
    assert email_parser_mock.parse_email_message.call_count == 1


def test_fetch_emails_specific_folder(
    protocol: ImapProtocol, imap_mock, folder_service_mock, monkeypatch
):
    imap_mock.search.return_value = [10]
    imap_mock.fetch.return_value = {10: {b"RFC822": b"M"}}

    monkeypatch.setattr(
        proto_mod.py_email, "message_from_bytes", MagicMock(side_effect=[FakeMsg("M", None)])
    )

    protocol._logged_in = True
    out = protocol.fetch_emails(folder="INBOX", since=None, flags=None)

    folder_service_mock.selected_folder.assert_called_once_with("INBOX")
    assert out == ["parsed:M"]


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
            proto_mod.RecipientService,
            "split_recipients",
            return_value=(["a@x.com"], ["c@x.com"], ["b@x.com"]),
        ) as split_mock,
        patch.object(
            proto_mod.MessageBuilder, "build_message", return_value=SimpleNamespace(msg=True)
        ) as build_mock,
        patch.object(proto_mod.MessageBuilder, "attach_files") as attach_mock,
    ):
        mail = DummyEmail(
            "S",
            "B",
            recipients=[1],
            attachments=[DummyAttachment("f1.txt"), DummyAttachment("f2.pdf")],
        )

        protocol.send_email(mail)
        smtp_sender_mock.validate_send_state.assert_called_once_with(True)
        split_mock.assert_called_once()
        build_mock.assert_called_once_with(
            subject="S", body="B", from_addr="user@example.com", to=["a@x.com"], cc=["c@x.com"]
        )
        attach_mock.assert_called_once()
        smtp_sender_mock.send.assert_called_once_with(
            SimpleNamespace(msg=True), ["a@x.com", "c@x.com", "b@x.com"]
        )


def test_send_email_no_recipients_raises(protocol: ImapProtocol, smtp_sender_mock):
    protocol._logged_in = True

    with patch.object(proto_mod.RecipientService, "split_recipients", return_value=([], [], [])):
        with pytest.raises(ValueError, match="No recipients provided"):
            protocol.send_email(DummyEmail("S", "B", recipients=[]))

    smtp_sender_mock.validate_send_state.assert_called_once_with(True)


def test_delete_email_hard_delete(protocol: ImapProtocol, imap_mock, folder_service_mock):
    protocol._logged_in = True
    folder_service_mock.get_user_folders.return_value = ["INBOX"]
    imap_mock.search.return_value = [42]

    protocol.delete_email("<id-1>", hard_delete=True)

    imap_mock.delete_messages.assert_called_once_with([42])
    imap_mock.expunge.assert_called_once()
    imap_mock.move.assert_not_called()
    imap_mock.add_flags.assert_not_called()


def test_delete_email_soft_with_trash(protocol: ImapProtocol, imap_mock, folder_service_mock):
    protocol._logged_in = True
    folder_service_mock.get_user_folders.return_value = ["INBOX"]
    folder_service_mock.get_trash_folder.return_value = "Trash"
    imap_mock.search.return_value = [7]

    protocol.delete_email("<id-7>", hard_delete=False)

    imap_mock.move.assert_called_once_with([7], "Trash")
    imap_mock.add_flags.assert_not_called()
    imap_mock.expunge.assert_not_called()


def test_delete_email_soft_without_trash(protocol: ImapProtocol, imap_mock, folder_service_mock):
    protocol._logged_in = True
    folder_service_mock.get_user_folders.return_value = ["INBOX"]
    folder_service_mock.get_trash_folder.return_value = None
    imap_mock.search.return_value = [9]

    protocol.delete_email("<id-9>", hard_delete=False)

    imap_mock.add_flags.assert_called_once_with([9], [b"\\Deleted"])
    imap_mock.move.assert_not_called()


def test_delete_email_not_found_in_first_folder_checks_next(
    protocol: ImapProtocol, imap_mock, folder_service_mock
):
    protocol._logged_in = True
    folder_service_mock.get_user_folders.return_value = ["INBOX", "Work"]
    imap_mock.search.side_effect = [[], [101]]

    protocol.delete_email("<id-101>", hard_delete=True)

    assert imap_mock.search.call_count == 2
    imap_mock.delete_messages.assert_called_once_with([101])
    imap_mock.expunge.assert_called_once()


def test_delete_email_requires_login(protocol: ImapProtocol):
    with pytest.raises(ee.NotLoggedIn):
        protocol.delete_email("<id>", hard_delete=True)


def test_tag_email_add_tag(protocol: ImapProtocol, imap_mock, folder_service_mock):
    """Test adding a tag to an email."""
    protocol._logged_in = True
    folder_service_mock.get_user_folders.return_value = ["INBOX"]
    imap_mock.search.return_value = [123]

    with patch("remail.interfaces.email.protocols.imap.TagService") as mock_tag_service_cls:
        mock_tag_service = MagicMock()
        mock_tag_service_cls.return_value = mock_tag_service

        protocol.tag_email("<test@example.com>", "important", remove=False)

        imap_mock.search.assert_called_once_with(["HEADER", "Message-ID", "<test@example.com>"])
        mock_tag_service_cls.assert_called_once_with(imap_mock)
        mock_tag_service.add_tag.assert_called_once_with(123, "important")
        mock_tag_service.remove_tag.assert_not_called()


def test_tag_email_remove_tag(protocol: ImapProtocol, imap_mock, folder_service_mock):
    """Test removing a tag from an email."""
    protocol._logged_in = True
    folder_service_mock.get_user_folders.return_value = ["INBOX"]
    imap_mock.search.return_value = [456]

    with patch("remail.interfaces.email.protocols.imap.TagService") as mock_tag_service_cls:
        mock_tag_service = MagicMock()
        mock_tag_service_cls.return_value = mock_tag_service

        protocol.tag_email("<test@example.com>", "work", remove=True)

        mock_tag_service.remove_tag.assert_called_once_with(456, "work")
        mock_tag_service.add_tag.assert_not_called()


def test_tag_email_multiple_uids(protocol: ImapProtocol, imap_mock, folder_service_mock):
    """Test tagging email when multiple UIDs are found."""
    protocol._logged_in = True
    folder_service_mock.get_user_folders.return_value = ["INBOX"]
    imap_mock.search.return_value = [123, 456, 789]

    with patch("remail.interfaces.email.protocols.imap.TagService") as mock_tag_service_cls:
        mock_tag_service = MagicMock()
        mock_tag_service_cls.return_value = mock_tag_service

        protocol.tag_email("<test@example.com>", "important", remove=False)

        # Should tag all UIDs
        assert mock_tag_service.add_tag.call_count == 3
        mock_tag_service.add_tag.assert_any_call(123, "important")
        mock_tag_service.add_tag.assert_any_call(456, "important")
        mock_tag_service.add_tag.assert_any_call(789, "important")


def test_tag_email_searches_multiple_folders(
    protocol: ImapProtocol, imap_mock, folder_service_mock
):
    """Test that tag_email searches across multiple folders."""
    protocol._logged_in = True
    folder_service_mock.get_user_folders.return_value = ["INBOX", "Work", "Archive"]
    imap_mock.search.side_effect = [[], [789], []]  # Found in second folder

    with patch("remail.interfaces.email.protocols.imap.TagService") as mock_tag_service_cls:
        mock_tag_service = MagicMock()
        mock_tag_service_cls.return_value = mock_tag_service

        protocol.tag_email("<test@example.com>", "important", remove=False)

        # Should search multiple folders until found
        assert imap_mock.search.call_count == 2
        mock_tag_service.add_tag.assert_called_once_with(789, "important")


def test_tag_email_not_found(protocol: ImapProtocol, imap_mock, folder_service_mock):
    """Test tagging email when message is not found."""
    protocol._logged_in = True
    folder_service_mock.get_user_folders.return_value = ["INBOX", "Work"]
    imap_mock.search.return_value = []

    with patch("remail.interfaces.email.protocols.imap.TagService") as mock_tag_service_cls:
        mock_tag_service = MagicMock()
        mock_tag_service_cls.return_value = mock_tag_service

        protocol.tag_email("<nonexistent@example.com>", "important", remove=False)

        # Should search all folders but not call tag service
        assert imap_mock.search.call_count == 2
        mock_tag_service.add_tag.assert_not_called()
        mock_tag_service.remove_tag.assert_not_called()


def test_tag_email_requires_login(protocol: ImapProtocol):
    """Test that tag_email raises NotLoggedIn when not authenticated."""
    with pytest.raises(ee.NotLoggedIn):
        protocol.tag_email("<test@example.com>", "important", remove=False)


def test_tag_email_with_standard_flag(protocol: ImapProtocol, imap_mock, folder_service_mock):
    """Test adding a standard IMAP flag."""
    protocol._logged_in = True
    folder_service_mock.get_user_folders.return_value = ["INBOX"]
    imap_mock.search.return_value = [123]

    with patch("remail.interfaces.email.protocols.imap.TagService") as mock_tag_service_cls:
        mock_tag_service = MagicMock()
        mock_tag_service_cls.return_value = mock_tag_service

        protocol.tag_email("<test@example.com>", "\\FLAGGED", remove=False)

        mock_tag_service.add_tag.assert_called_once_with(123, "\\FLAGGED")
