from enum import Enum


class Timezone(str, Enum):
    EUROPE_BERLIN = "Europe/Berlin (UTC+01:00)"


__all__ = ["Timezone"]
