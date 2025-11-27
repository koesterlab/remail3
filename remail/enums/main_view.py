from enum import Enum


class MainView(str, Enum):
    """Enum for top-level view keys in the application."""

    SETTINGS = "settings"
    EMAIL = "email"
    DASHBOARD = "dashboard"
