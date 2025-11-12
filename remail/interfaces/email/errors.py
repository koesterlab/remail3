"""Custom exceptions for email protocol operations."""


class EmailError(Exception):
    """Base exception for all email-related errors."""

    pass


class InvalidLoginData(EmailError):
    """Raised when login credentials are invalid or missing."""

    pass


class NotLoggedIn(EmailError):
    """Raised when attempting an operation that requires authentication."""

    pass


class ServerConnectionFail(EmailError):
    """Raised when connection to email server fails."""

    pass


class SMTPDataFalse(EmailError):
    """Raised when SMTP data command fails."""

    pass


class RecipientsFail(EmailError):
    """Raised when email recipient addresses are invalid."""

    pass


class UnknownError(EmailError):
    """Raised for unexpected errors that don't fit other categories."""

    pass
