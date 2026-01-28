"""User service for managing email account users."""

from sqlmodel import Session, select

from remail.controllers.dtos.user_dto import UserDTO
from remail.database.db import engine
from remail.enums import UserAccountCategory
from remail.models.user import User


class UserService:
    """Service for managing user accounts in the database."""

    @staticmethod
    def count_unread(user: User) -> int:
        """
        Count unread conversations for a user.

        Args:
            user: User object

        Returns:
            Number of unread conversations (placeholder, implement later)
        """
        # TODO: Implement actual unread count from UserConversation
        return 0

    @staticmethod
    def user_to_dto(user: User) -> UserDTO:
        """
        Convert User model to UserDTO
        Args:
            user: User ORM object

        Returns:
            UserDTO object
        """
        if user.id is None:
            raise ValueError("User must have an ID")

        return UserDTO(
            id=user.id,
            name=user.name,
            email=user.email,
            host=user.host,
            password=user.password,
            category=UserAccountCategory.PRIVATE,  # User model doesn't have category
            protocol=user.protocol,
            unread_conversations=UserService.count_unread(user),
        )

    @staticmethod
    def get_user_by_email(email: str) -> User | None:
        """
        Get user by email address.

        Args:
            email: Email address to search for

        Returns:
            User object if found, None otherwise
        """
        with Session(engine) as session:
            statement = select(User).where(User.email == email)
            return session.exec(statement).first()

    @staticmethod
    def get_all_users() -> list[UserDTO]:
        """
        Get all users from the database as DTOs.

        Returns:
            List of all UserDTO objects
        """
        with Session(engine) as session:
            statement = select(User)
            results = session.exec(statement).all()
            return [UserService.user_to_dto(user) for user in results]
