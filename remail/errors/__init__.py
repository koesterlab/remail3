"""Custom exceptions for email protocol operations."""

from .email_error import EmailError
from .handlers import email_error_handler
from .invalid_login_data import InvalidLoginData
from .not_logged_in import NotLoggedIn
from .recipients_fail import RecipientsFail
from .server_connection_fail import ServerConnectionFail
from .unknown_error import UnknownError

__all__ = [
    "EmailError",
    "InvalidLoginData",
    "NotLoggedIn",
    "RecipientsFail",
    "ServerConnectionFail",
    "UnknownError",
    "email_error_handler",
]
