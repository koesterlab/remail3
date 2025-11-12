"""Exception raised for unexpected errors that don't fit other categories."""

from .email_error import EmailError


class UnknownError(EmailError):
    """Raised for unexpected errors that don't fit other categories."""

    pass


__all__ = ["UnknownError"]
