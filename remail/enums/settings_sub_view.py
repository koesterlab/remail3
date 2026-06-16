from enum import Enum


class SettingsSubView(Enum):
    APPEARANCE = "appearance"
    EMAIL_ACCOUNTS = "email_accounts"
    LANGUAGE = "language"
    NOTIFICATIONS = "notifications"
    TAGS = "tags"


__all__ = ["SettingsSubView"]
