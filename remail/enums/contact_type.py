from enum import Enum


class ContactType(Enum):
    BUSINESS = "business"
    PRIVATE = "private"
    COMPANY = "company"
    NEWSLETTER = "newsletter"


__all__ = ["ContactType"]
