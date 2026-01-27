from remail.errors import (
    EmailError,
    InvalidLoginData,
    NotLoggedIn,
    RecipientsFail,
    ServerConnectionFail,
    UnknownError,
    email_error_handler,
)
from remail.interfaces.email.protocols.base import EmailProtocol
from remail.interfaces.email.protocols.imap import ImapProtocol
from remail.interfaces.email.services.attachment_service import save_attachment

__all__ = [
    "EmailProtocol",
    "email_error_handler",
    "ImapProtocol",
    "save_attachment",
    "EmailError",
    "InvalidLoginData",
    "NotLoggedIn",
    "ServerConnectionFail",
    "RecipientsFail",
    "UnknownError",
]
