from enum import Enum


class Timezone(str, Enum):
    """Enum for popular timezones."""

    AMERICA_NEW_YORK = "America/New_York (UTC-05:00)"
    AMERICA_CHICAGO = "America/Chicago (UTC-06:00)"
    AMERICA_LOS_ANGELES = "America/Los_Angeles (UTC-08:00)"
    EUROPE_LONDON = "Europe/London (UTC+00:00)"
    EUROPE_BERLIN = "Europe/Berlin (UTC+01:00)"
    EUROPE_MOSCOW = "Europe/Moscow (UTC+03:00)"
    ASIA_DUBAI = "Asia/Dubai (UTC+04:00)"
    ASIA_SHANGHAI = "Asia/Shanghai (UTC+08:00)"
    ASIA_TOKYO = "Asia/Tokyo (UTC+09:00)"
    AUSTRALIA_SYDNEY = "Australia/Sydney (UTC+11:00)"
    PACIFIC_AUCKLAND = "Pacific/Auckland (UTC+13:00)"
