from dataclasses import dataclass

from remail.enums import Protocol, UserAccountCategory
from remail.models import User


@dataclass
class UserDTO:
    id: int
    name: str
    email: str
    category: UserAccountCategory
    protocol: Protocol
    unread_conversations: int

    def __eq__(self, other):
        return self.id == other.id

    @staticmethod
    def get_from_model(user: User, unread_count: int) -> "UserDTO":
        return UserDTO(
            email=user.email,
            id=user.id if user.id else -1,
            name=user.name,
            category=UserAccountCategory.PRIVATE,
            protocol=user.protocol,
            unread_conversations=unread_count,

        )
