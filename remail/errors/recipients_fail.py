"""Exception raised when email recipient addresses are invalid."""

from .email_error import EmailError


class RecipientsFail(EmailError):
    """Raised when email recipient addresses are invalid."""

    pass


__all__ = ["RecipientsFail"]
