from contextlib import contextmanager
from datetime import datetime

from imapclient import IMAPClient


class FolderService:
    """Manages IMAP folder selection and search criteria."""

    def __init__(self, client: IMAPClient):
        self._client = client

    def get_all_folders(self) -> list[str]:
        return [info[2] for info in self._client.list_folders()]

    @contextmanager
    def selected_folder(self, name: str):
        self._client.select_folder(name)
        try:
            yield
        finally:
            pass

    @staticmethod
    def build_search_criteria(since: datetime | None, flags: list[str] | None) -> list:
        criteria = (["SINCE", since.date()] if since else []) + (flags or [])
        return criteria or ["ALL"]
