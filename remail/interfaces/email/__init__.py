from importlib import import_module

from remail.errors import (
    EmailError,
    InvalidLoginData,
    NotLoggedIn,
    RecipientsFail,
    ServerConnectionFail,
    UnknownError,
    email_error_handler,
)

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

_LAZY_IMPORTS = {
    "EmailProtocol": "remail.interfaces.email.protocols.base",
    "ImapProtocol": "remail.interfaces.email.protocols.imap",
    "save_attachment": "remail.interfaces.email.services.attachment_service",
}


def __getattr__(name: str):
    if name in _LAZY_IMPORTS:
        module = import_module(_LAZY_IMPORTS[name])
        return getattr(module, name)
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


def __dir__():
    return sorted(list(globals().keys()) + list(_LAZY_IMPORTS.keys()))
