"""Exception raised when connection to email server fails."""

from .email_error import EmailError


class ServerConnectionFail(EmailError):
    """Raised when connection to email server fails."""

    pass


__all__ = ["ServerConnectionFail"]
