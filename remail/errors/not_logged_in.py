from .email_error import EmailError


class NotLoggedIn(EmailError):
    pass


__all__ = ["NotLoggedIn"]
