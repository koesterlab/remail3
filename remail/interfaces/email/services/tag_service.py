"""Service for managing email tags/labels."""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from imapclient import IMAPClient  # type: ignore


class TagService:
    """Service for handling email tags/labels using IMAP keywords."""

    def __init__(self, imap_client: "IMAPClient"):
        """
        Initialize TagService.

        Args:
            imap_client: IMAP client instance
        """
        self.IMAP = imap_client

    def add_tag(self, uid: int, tag: str) -> None:
        """
        Add a tag/keyword to an email.

        Args:
            uid: Email UID
            tag: Tag name to add (will be prefixed with $ if not a standard flag)

        Note:
            IMAP keywords are case-insensitive and typically stored with a $ prefix
            for custom keywords.
        """

        if not tag.startswith("$") and tag.upper() not in [
            "\\SEEN",
            "\\ANSWERED",
            "\\FLAGGED",
            "\\DELETED",
            "\\DRAFT",
            "\\RECENT",
        ]:
            tag = f"${tag}"

        self.IMAP.add_flags([uid], [tag.encode() if isinstance(tag, str) else tag])

    def remove_tag(self, uid: int, tag: str) -> None:
        """
        Remove a tag/keyword from an email.

        Args:
            uid: Email UID
            tag: Tag name to remove
        """

        if not tag.startswith("$") and tag.upper() not in [
            "\\SEEN",
            "\\ANSWERED",
            "\\FLAGGED",
            "\\DELETED",
            "\\DRAFT",
            "\\RECENT",
        ]:
            tag = f"${tag}"

        self.IMAP.remove_flags([uid], [tag.encode() if isinstance(tag, str) else tag])

    def get_tags(self, uid: int) -> list[str]:
        """
        Get all tags/keywords for an email.

        Args:
            uid: Email UID

        Returns:
            List of tag names
        """

        fetch_data = self.IMAP.fetch([uid], ["FLAGS"])

        if uid in fetch_data:
            flags = fetch_data[uid].get(b"FLAGS", [])
            custom_tags = []

            for flag in flags:
                flag_str = flag.decode() if isinstance(flag, bytes) else str(flag)

                if flag_str.startswith("$") or flag_str.startswith("\\"):
                    custom_tags.append(flag_str)

            return custom_tags

        return []

    def search_by_tag(self, tag: str, folder: str | None = None) -> list[int]:
        """
        Search for emails with a specific tag.

        Args:
            tag: Tag name to search for
            folder: Optional folder to search in (if None, searches current folder)

        Returns:
            List of email UIDs matching the tag
        """

        if not tag.startswith("$") and tag.upper() not in [
            "\\SEEN",
            "\\ANSWERED",
            "\\FLAGGED",
            "\\DELETED",
            "\\DRAFT",
            "\\RECENT",
        ]:
            tag = f"${tag}"

        # IMAP KEYWORD search
        result: list[int] = self.IMAP.search(["KEYWORD", tag])
        return result
