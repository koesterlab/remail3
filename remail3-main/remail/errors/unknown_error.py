from .email_error import EmailError


class UnknownError(EmailError):
    pass


__all__ = ["UnknownError"]
