from .email_error import EmailError


class RecipientsFail(EmailError):
    pass


__all__ = ["RecipientsFail"]
