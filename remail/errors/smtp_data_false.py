"""Exception raised when SMTP data command fails."""

from .email_error import EmailError


class SMTPDataFalse(EmailError):
    """Raised when SMTP data command fails."""

    pass


__all__ = ["SMTPDataFalse"]
