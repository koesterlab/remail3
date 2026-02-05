from enum import Enum


class AuthMethods(Enum):
    PASSWORD = "password"
    ENCRYPTED_PASSWORD = "encrypted_password"
    OAUTH = "oauth"