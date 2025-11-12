"""Email interface package - Protocol implementations for email operations."""

from remail.interfaces.email.errors import (
    EmailError,
    InvalidLoginData,
    NotLoggedIn,
    RecipientsFail,
    ServerConnectionFail,
    SMTPDataFalse,
    UnknownError,
)
from remail.interfaces.email.protocols.base import EmailProtocol, error_handler
from remail.interfaces.email.protocols.imap import ImapProtocol
from remail.interfaces.email.services.attachment_service import save_attachment
from remail.interfaces.email.utils.helpers import (
    create_email,
    parse_permission_string,
)

__all__ = [
    "EmailProtocol",
    "error_handler",
    "ImapProtocol",
    "create_email",
    "save_attachment",
    "parse_permission_string",
    "EmailError",
    "InvalidLoginData",
    "NotLoggedIn",
    "ServerConnectionFail",
    "SMTPDataFalse",
    "RecipientsFail",
    "UnknownError",
]
