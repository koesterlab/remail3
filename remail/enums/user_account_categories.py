from enum import Enum


class UserAccountCategory(Enum):
    PRIVATE = "private",
    WORK = "work",
    HOBBY = "hobby",
    NOT_SPECIFIED = "not_specified"