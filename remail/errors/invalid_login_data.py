from .email_error import EmailError


class InvalidLoginData(EmailError):
    pass


__all__ = ["InvalidLoginData"]
