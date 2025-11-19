"""Base protocol interface for email services."""

from abc import ABC, abstractmethod
from datetime import datetime
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from remail.models import Email


class EmailProtocol(ABC):
    """Abstract base class for email protocol implementations (IMAP, Exchange, etc.)."""

    @property
    @abstractmethod
    def logged_in(self) -> bool:
        """Return True if user is logged in, False otherwise."""

        pass

    @abstractmethod
    def login(self) -> None:
        """Log in user with credentials."""

        pass

    @abstractmethod
    def logout(self) -> None:
        """Log out the user."""

        pass

    @abstractmethod
    def fetch_emails(self, date: datetime | None = None) -> list["Email"]:
        """
        Retrieve emails from server.

        Args:
            date: If provided, only return emails after this datetime.
                  Must include timezone information.

        Returns:
            List of Email objects
        """

        pass

    @abstractmethod
    def send_email(self, email: "Email") -> None:
        """Send the given email."""

        pass

    @abstractmethod
    def delete_email(self, message_id: str, hard_delete: bool = False) -> None:
        """
        Delete email.

        Args:
            message_id: The message ID to delete
            hard_delete: If True, permanently delete; if False, move to trash
        """

        pass

    @abstractmethod
    def tag_email(self, message_id: str, tag: str, remove: bool = False) -> None:
        """
        Add or remove a tag from an email.

        Args:
            message_id: The message ID to tag
            tag: Tag name to add or remove
            remove: If True, remove the tag; if False, add it
        """

        pass
