from enum import Enum


class ThemeMode(str, Enum):
    """Enum for theme modes."""

    LIGHT = "light"
    DARK = "dark"
    SYSTEM = "system"
