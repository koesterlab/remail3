from enum import Enum


class MainView(Enum):
    SETTINGS = "settings"
    EMAIL = "email"
    DASHBOARD = "dashboard"
    CHATBOT = "chatbot"


__all__ = ["MainView"]
