from enum import Enum


class AuthMethods(Enum):
    PASSWORD = "password"  # nosec
    ENCRYPTED_PASSWORD = "encrypted_password"  # nosec
    OAUTH = "oauth"  # nosec
