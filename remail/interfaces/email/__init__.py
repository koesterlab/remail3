"""Email interface package - Protocol implementations for email operations."""

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
from remail.interfaces.email.services.email_factory_service import (
    EmailFactory,
)
from remail.interfaces.email.services.permission_service import PermissionService

__all__ = [
    "EmailProtocol",
    "email_error_handler",
    "ImapProtocol",
    "EmailFactory",
    "save_attachment",
    "PermissionService",
    "EmailError",
    "InvalidLoginData",
    "NotLoggedIn",
    "ServerConnectionFail",
    "RecipientsFail",
    "UnknownError",
]
