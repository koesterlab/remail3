from abc import ABC, abstractmethod
from datetime import datetime
from email.message import Message
from typing import TYPE_CHECKING, AsyncGenerator, Any

if TYPE_CHECKING:
    from remail.models import Email


class EmailProtocol(ABC):
    """Abstract base class for email protocol implementations (IMAP, Exchange, etc.)."""

    @abstractmethod
    def test_connection(self) -> bool:
        """Log in user with credentials."""

        pass

    @abstractmethod
    def fetch_emails(self, new_only:bool = True) -> dict:
        """
        Retrieve emails from server.

        Args:
            new_only: if false, all mails are returned (e.g. for resync), otherwise only new since last fetch

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

    @abstractmethod
    def wait_for_changes(self) -> AsyncGenerator[Any, None]:
        """Waits for live-updates (e.g. with imap idle)"""
        pass

    @abstractmethod
    def serialize(self) -> str:
        """Serialize to store in database"""

    @abstractmethod
    def deserialize(self, string: str) -> None:
        """Restores the values from a serialized string"""