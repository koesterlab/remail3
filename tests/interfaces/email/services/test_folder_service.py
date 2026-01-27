from datetime import datetime
from unittest.mock import MagicMock

import pytest
from imapclient import IMAPClient

from remail.interfaces.email.services.folder_service import FolderService


@pytest.fixture
def imap_mock() -> IMAPClient:
    return MagicMock(spec=IMAPClient)


@pytest.fixture
def service(imap_mock: IMAPClient) -> FolderService:
    return FolderService(imap_client=imap_mock)


def test_get_user_folders_excludes_system_and_trash_by_default(
    service: FolderService, imap_mock: IMAPClient
):
    imap_mock.list_folders.return_value = [
        ([b"\\HasChildren"], "/", "Parent"),
        ([b"\\Drafts"], "/", "Drafts"),
        ([b"\\Junk"], "/", "Spam"),
        ([b"\\Noselect"], "/", "NoSelect"),
        ([b"\\All"], "/", "All Mail"),
        ([b"\\Trash"], "/", "Trash"),
        ([], "/", "INBOX"),
        ([], "/", "Archive"),
        ([b"\\Flagged"], "/", "Starred"),
    ]

    folders = service.get_user_folders()

    assert folders == ["INBOX", "Archive", "Starred"]


def test_get_user_folders_includes_trash_when_requested(
    service: FolderService, imap_mock: IMAPClient
):
    imap_mock.list_folders.return_value = [
        ([b"\\Trash"], "/", "Trash"),
        ([], "/", "INBOX"),
    ]

    folders = service.get_user_folders(include_trash=True)

    assert folders == ["Trash", "INBOX"]


@pytest.mark.parametrize(
    "since,flags,expected_prefix",
    [
        (None, None, ["ALL"]),
        (datetime(2025, 1, 2, 15, 30, 0), None, ["SINCE", datetime(2025, 1, 2).date()]),
        (None, ["UNSEEN"], ["UNSEEN"]),
        (
            datetime(2025, 1, 2, 23, 59, 59),
            ["SEEN"],
            ["SINCE", datetime(2025, 1, 2).date(), "SEEN"],
        ),
    ],
)
def test_build_search_criteria(since, flags, expected_prefix):
    crit = FolderService.build_search_criteria(since, flags)

    assert crit[: len(expected_prefix)] == expected_prefix

    if since is None and flags is None:
        assert crit == ["ALL"]


def test_selected_folder_enters_and_closes(service: FolderService, imap_mock: IMAPClient):
    with service.selected_folder("INBOX"):
        pass

    imap_mock.select_folder.assert_called_once_with("INBOX")
    imap_mock.close_folder.assert_called_once()


def test_selected_folder_closes_even_on_exception(service: FolderService, imap_mock: IMAPClient):
    class Boom(Exception):
        pass

    with pytest.raises(Boom):
        with service.selected_folder("INBOX"):
            raise Boom("fail inside context")

    imap_mock.select_folder.assert_called_once_with("INBOX")
    imap_mock.close_folder.assert_called_once()
