"""Exception raised when login credentials are invalid or missing."""

from .email_error import EmailError


class InvalidLoginData(EmailError):
    """Raised when login credentials are invalid or missing."""

    pass


__all__ = ["InvalidLoginData"]
