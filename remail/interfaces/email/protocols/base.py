from abc import ABC, abstractmethod
from datetime import datetime

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
    def fetch_emails(
        self,
        folder: str | None = None,
        since: datetime | None = None,
        flags: list[str] | None = None,
    ) -> list[Email]:
        """
        Retrieve emails from server.

        Args:
            folder: Optional mailbox name. If None, fetch from all user folders.
            since: If provided, only return emails after this datetime.
                Must include timezone information.
            flags: Optional IMAP search terms (e.g., ["UNSEEN"], ["SEEN"],
                ["DELETED"], ["HEADER", "From", "x@y"]).

        Returns:
            List of Email objects
        """

        pass

    @abstractmethod
    def send_email(self, email: "Email") -> None:
        """Send the given email."""

        pass
