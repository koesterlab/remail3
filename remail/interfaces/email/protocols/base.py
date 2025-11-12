"""Base protocol interface for email services."""

from abc import ABC, abstractmethod
from datetime import datetime
from functools import wraps
from smtplib import (
    SMTPAuthenticationError,
    SMTPConnectError,
    SMTPDataError,
    SMTPHeloError,
    SMTPRecipientsRefused,
    SMTPServerDisconnected,
)
from typing import TYPE_CHECKING

from exchangelib import errors as exch_errors  # type: ignore
from imapclient.exceptions import (  # type: ignore
    CapabilityError,
    IMAPClientAbortError,
    IMAPClientError,
    LoginError,
)

from remail import errors as ee

if TYPE_CHECKING:
    from remail.models import Email


def error_handler(func):
    """Decorator to handle common email protocol errors and convert them to custom exceptions."""

    @wraps(func)
    def wrapper(self, *args, **kwargs):
        RECIPIENTSFAIL = (SMTPRecipientsRefused, exch_errors.ErrorInvalidRecipients)
        CONNECTIONFAIL = (
            SMTPConnectError,
            exch_errors.ErrorConnectionFailed,
            exch_errors.TransportError,
            SMTPServerDisconnected,
            SMTPHeloError,
            IMAPClientError,
            IMAPClientAbortError,
            CapabilityError,
        )
        INVALIDLOGINDATA = (
            exch_errors.UnauthorizedError,
            LoginError,
            SMTPAuthenticationError,
        )

        try:
            return func(self, *args, **kwargs)
        except ee.EmailError as e:
            raise e
        except ValueError as e:
            if "is not an email address" in str(e):
                raise ee.InvalidLoginData() from e
            else:
                raise ee.UnknownError(f"An unexpected error occurred: {str(e)}") from e
        except INVALIDLOGINDATA as e:
            raise ee.InvalidLoginData() from e
        except CONNECTIONFAIL as e:
            raise ee.ServerConnectionFail() from e
        except SMTPDataError as e:
            raise ee.SMTPDataFalse() from e
        except RECIPIENTSFAIL as e:
            raise ee.RecipientsFail() from e
        except Exception as e:
            raise ee.UnknownError(f"An unexpected error occurred: {str(e)}") from e

    return wrapper


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
