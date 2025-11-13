"""Exception raised when attempting an operation that requires authentication."""

from .email_error import EmailError


class NotLoggedIn(EmailError):
    """Raised when attempting an operation that requires authentication."""

    pass


__all__ = ["NotLoggedIn"]
