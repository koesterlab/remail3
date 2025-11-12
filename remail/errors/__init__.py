"""Custom exceptions for email protocol operations."""

from .email_error import EmailError
from .invalid_login_data import InvalidLoginData
from .not_logged_in import NotLoggedIn
from .recipients_fail import RecipientsFail
from .server_connection_fail import ServerConnectionFail
from .smtp_data_false import SMTPDataFalse
from .unknown_error import UnknownError

__all__ = [
    "EmailError",
    "InvalidLoginData",
    "NotLoggedIn",
    "RecipientsFail",
    "ServerConnectionFail",
    "SMTPDataFalse",
    "UnknownError",
]
