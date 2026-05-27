from enum import Enum


class ThemeMode(Enum):
    LIGHT = "light"
    DARK = "dark"
    SYSTEM = "system"

    @classmethod
    def _missing_(cls, value):
        if isinstance(value, str):
            # Eğer değer 'ThemeMode.LIGHT' veya 'LIGHT' gibi gelirse temizleyip küçük harfe çevirir
            clean_value = value.replace("ThemeMode.", "").lower()
            for member in cls:
                if member.value == clean_value:
                    return member
        return super()._missing_(value)


__all__ = ["ThemeMode"]