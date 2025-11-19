from contextlib import contextmanager
from datetime import datetime

from imapclient import IMAPClient


class FolderService:
    """Service for managing IMAP folders and search operations."""

    def __init__(self, imap_client: IMAPClient):
        """
        Initialize folder service.

        Args:
            imap_client: IMAPClient instance to use
        """

        self.imap_client = imap_client

    def get_user_folders(self, *, include_trash: bool = False) -> list[str]:
        """
        Get list of user folders, excluding system folders.

        Args:
            include_trash: Whether to include trash folder

        Returns:
            List of folder names
        """

        excluded = {b"\\HasChildren", b"\\Drafts", b"\\Junk", b"\\Noselect", b"\\All"}

        if not include_trash:
            excluded.add(b"\\Trash")

        return [
            name
            for flags, _, name in self.imap_client.list_folders()
            if not (set(flags) & excluded)
        ]

    def get_trash_folder(self) -> str | None:
        """
        Find the trash folder.

        Returns:
            Trash folder name or None if not found
        """

        for flags, _, name in self.imap_client.list_folders():
            if b"\\Trash" in set(flags):
                return str(name)

        return None

    @staticmethod
    def build_search_criteria(since: datetime | None, flags: list[str] | None) -> list:
        """
        Build IMAP search criteria.

        Args:
            since: Filter emails since this datetime
            flags: IMAP search flags

        Returns:
            List of search criteria
        """

        crit: list = []

        if since:
            crit += ["SINCE", since.date()]  # IMAP SINCE is date-based

        if flags:
            crit += flags

        return crit or ["ALL"]

    @contextmanager
    def selected_folder(self, name: str):
        """
        Context manager for selecting and closing a folder.

        Args:
            name: Folder name to select

        Yields:
            None
        """

        self.imap_client.select_folder(name)

        try:
            yield

        finally:
            self.imap_client.close_folder()
