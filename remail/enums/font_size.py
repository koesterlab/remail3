from enum import Enum


class FontSize(str, Enum):
    SMALL = "Small"
    MEDIUM = "Medium"
    LARGE = "Large"


__all__ = ["FontSize"]
