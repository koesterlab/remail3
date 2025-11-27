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
        RECIPIENTSFAIL = (SMTPRecipientsRefused,)
        CONNECTIONFAIL = (
            SMTPConnectError,
            SMTPServerDisconnected,
            SMTPHeloError,
            IMAPClientError,
            IMAPClientAbortError,
            CapabilityError,
        )
        INVALIDLOGINDATA = (
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


__all__ = ["email_error_handler"]
