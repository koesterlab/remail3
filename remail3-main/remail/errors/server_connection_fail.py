from .email_error import EmailError


class ServerConnectionFail(EmailError):
    pass


__all__ = ["ServerConnectionFail"]
