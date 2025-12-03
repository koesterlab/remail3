"""Email error handler decorator."""

from functools import wraps
from smtplib import (
    SMTPAuthenticationError,
    SMTPConnectError,
    SMTPDataError,
    SMTPHeloError,
    SMTPRecipientsRefused,
    SMTPServerDisconnected,
)

from imapclient.exceptions import (
    CapabilityError,
    IMAPClientAbortError,
    IMAPClientError,
    LoginError,
)

from remail import errors as ee


def email_error_handler(func):
    """Decorator to handle common email protocol errors and convert them to custom exceptions."""

    @wraps(func)
    def wrapper(self, *args, **kwargs):
        _RECIPIENTS_FAIL = (SMTPRecipientsRefused,)
        _CONNECTION_FAIL = (
            SMTPConnectError,
            SMTPServerDisconnected,
            SMTPHeloError,
            IMAPClientError,
            IMAPClientAbortError,
            CapabilityError,
        )
        _INVALID_LOGIN_DATA = (
            LoginError,
            SMTPAuthenticationError,
            SMTPDataError,
        )

        try:
            return func(self, *args, **kwargs)

        except ee.EmailError as e:
            raise e

        except ValueError as e:
            if "is not an email address" in str(e):
                raise ee.InvalidLoginData() from e

            raise ee.UnknownError(f"An unexpected error occurred: {str(e)}") from e

        except _INVALID_LOGIN_DATA as e:
            raise ee.InvalidLoginData() from e

        except _CONNECTION_FAIL as e:
            raise ee.ServerConnectionFail() from e

        except _RECIPIENTS_FAIL as e:
            raise ee.RecipientsFail() from e

        except Exception as e:
            raise ee.UnknownError(f"An unexpected error occurred: {str(e)}") from e

    return wrapper


__all__ = ["email_error_handler"]
