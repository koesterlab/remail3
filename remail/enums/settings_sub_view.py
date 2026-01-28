from enum import Enum


class SettingsSubView(str, Enum):
    APPEARANCE = "appearance"
    EMAIL_ACCOUNTS = "email_accounts"
    LANGUAGE = "language"
    NOTIFICATIONS = "notifications"


__all__ = ["SettingsSubView"]
