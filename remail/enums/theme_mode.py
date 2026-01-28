from enum import Enum


class ThemeMode(str, Enum):
    LIGHT = "light"
    DARK = "dark"
    SYSTEM = "system"


__all__ = ["ThemeMode"]
