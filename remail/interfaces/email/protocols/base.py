from abc import ABC, abstractmethod
from datetime import datetime
from email.message import Message
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
    def fetch_emails(self, since: datetime | None = None) -> list[tuple[int, Message]]:
        """
        Retrieve emails from server.

        Args:
            since: If provided, only return emails after this datetime.
                  Must include timezone information.

        Returns:
            List of (uid, email message) tuples
        """

        pass

    @abstractmethod
    def send_email(self, email: "Email") -> None:
        """Send the given email."""
        pass

    @abstractmethod
    def clone(self) -> "EmailProtocol":
        """Clones the instance"""
        pass
