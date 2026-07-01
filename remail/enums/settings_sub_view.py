from enum import Enum


class SettingsSubView(Enum):
    APPEARANCE = "appearance"
    ATTACHMENTS = "attachments"
    EMAIL_ACCOUNTS = "email_accounts"
    LANGUAGE = "language"
    NOTIFICATIONS = "notifications"
    LOCAL_MODELS = "local_models"


__all__ = ["SettingsSubView"]
