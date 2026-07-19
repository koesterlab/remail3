from enum import Enum


class SettingsSubView(Enum):
    APPEARANCE = "appearance"
    ATTACHMENTS = "attachments"
    EMAIL_ACCOUNTS = "email_accounts"
    LANGUAGE = "language"
    NOTIFICATIONS = "notifications"
    TAGS = "tags"


__all__ = ["SettingsSubView"]
