from dataclasses import dataclass

from remail.enums import Protocol, UserAccountCategory


@dataclass
class UserDTO:
    id: int
    name: str
    username: str
    host: str
    password: str
    category: UserAccountCategory
    protocol: Protocol
    unread_conversations: int
