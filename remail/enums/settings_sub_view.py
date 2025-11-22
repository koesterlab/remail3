from enum import Enum


class SettingsSubView(str, Enum):
    """Enum for settings sub-views."""

    APPEARANCE = "appearance"
    EMAIL_ACCOUNTS = "email_accounts"
    LANGUAGE = "language"
    ACCOUNT = "account"
    NOTIFICATIONS = "notifications"
