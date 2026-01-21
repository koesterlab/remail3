"""User service for managing email account users."""

from sqlmodel import Session, select

from remail.controllers.dtos.user_dto import UserDTO
from remail.database.db import engine
from remail.enums import Protocol, UserAccountCategory
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
    def add_user(
        email: str,
        password: str,
        host: str,
        name: str | None = None,
        protocol: Protocol = Protocol.IMAP,
    ) -> User:
        """
        Add a new user to the database.

        Args:
            email: User's email address (must be unique)
            password: User's password (should be hashed before passing!)
            host: IMAP/SMTP server hostname
            name: User's display name (optional, defaults to email username part)
            protocol: Email protocol (default: IMAP)

        Returns:
            Created User object

        Raises:
            ValueError: If user with this email already exists
        """
        with Session(engine) as session:
            # Check if user with this email already exists
            statement = select(User).where(User.email == email)
            existing = session.exec(statement).first()

            if existing:
                raise ValueError(f"User with email '{email}' already exists")

            # If name not provided, extract from email
            if name is None:
                name = email.split("@")[0]

            # Create new user
            new_user = User(
                name=name,
                email=email,
                host=host,
                password=password,
                protocol=protocol,
            )

            session.add(new_user)
            session.commit()
            session.refresh(new_user)

            return new_user

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
    def get_user_by_id(user_id: int) -> User | None:
        """
        Get user by ID.

        Args:
            user_id: User ID to search for

        Returns:
            User object if found, None otherwise
        """
        with Session(engine) as session:
            statement = select(User).where(User.id == user_id)
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

    @staticmethod
    def update_user(
        user_id: int,
        name: str | None = None,
        email: str | None = None,
        host: str | None = None,
        password: str | None = None,
        protocol: Protocol | None = None,
    ) -> User | None:
        """
        Update user information.

        Args:
            user_id: ID of user to update
            name: New name (optional)
            email: New email (optional)
            host: New host (optional)
            password: New password (optional, should be hashed!)
            protocol: New protocol (optional)

        Returns:
            Updated User object, or None if user not found

        Raises:
            ValueError: If trying to change email to one that already exists
        """
        with Session(engine) as session:
            statement = select(User).where(User.id == user_id)
            user = session.exec(statement).first()

            if not user:
                return None

            # Check if new email is already taken by another user
            if email and email != user.email:
                existing = session.exec(select(User).where(User.email == email)).first()
                if existing:
                    raise ValueError(f"Email '{email}' is already taken by another user")

            # Update fields if provided
            if name is not None:
                user.name = name
            if email is not None:
                user.email = email
            if host is not None:
                user.host = host
            if password is not None:
                user.password = password
            if protocol is not None:
                user.protocol = protocol

            session.add(user)
            session.commit()
            session.refresh(user)

            return user

    @staticmethod
    def delete_user(email: str) -> bool:
        """
        Delete user by email address.

        Args:
            email: Email of user to delete

        Returns:
            True if user was deleted, False if user was not found
        """
        with Session(engine) as session:
            statement = select(User).where(User.email == email)
            user = session.exec(statement).first()

            if user:
                session.delete(user)
                session.commit()
                return True

            return False

    @staticmethod
    def delete_user_by_id(user_id: int) -> bool:
        """
        Delete user by ID.

        Args:
            user_id: ID of user to delete

        Returns:
            True if user was deleted, False if user was not found
        """
        with Session(engine) as session:
            statement = select(User).where(User.id == user_id)
            user = session.exec(statement).first()

            if user:
                session.delete(user)
                session.commit()
                return True

            return False
