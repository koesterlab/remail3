"""User service for managing email account users."""

import logging
import json
from sqlmodel import Session, select

from remail.controllers.dtos.user_dto import UserDTO
from remail.enums import Protocol
from remail.interfaces.email import EmailProtocol
from remail.models.user import User
from remail.utils.session_management import session

_KEYRING_SERVICE = "remail"
_REDACTED_VALUE = "<redacted>"
_logger = logging.getLogger(__name__)


class UserService:
    """Service for managing user accounts in the database."""


    @staticmethod
    @session
    def update_user(
            user_id: int,
            name: str,
            password: str,
            session: Session,
    ) -> None:
        user = session.get(User, user_id)

        if not user:
            raise ValueError("User not found")

        # Update display name
        user.name = name

        # Update password inside serialized connection
        connection = json.loads(user.connection)
        connection["imap_password"] = password

        user.connection = json.dumps(connection)

        session.add(user)
        session.commit()


    @staticmethod
    @session
    def count_unread(user: User, session: Session) -> int:
        """
        Count unread conversations for a user.

        Args:
            user: User object

        Returns:
            Number of unread conversations (placeholder, implement later)
        """
        u = session.get(User, user.id)
        if not u:
            return 0
        return len([t for c in u.conversations for t in c.threads if t.unread_count > 0])

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

        return UserDTO.get_from_model(user, UserService.count_unread(user))
    @staticmethod
    @session
    def get_connection_by_user_id(user_id: int, session: Session) -> str | None:
        user = session.get(User, user_id)

        if not user:
            return None

        return user.connection
    @staticmethod
    @session
    def get_user_by_id(user_id: int, session: Session) -> User | None:
        return session.get(User, user_id)

    @staticmethod
    @session
    def get_user_by_email(email: str, session: Session) -> User | None:
        """Backward-compatible alias for username lookup."""
        return session.exec(select(User).where(User.email == email)).first()

    @staticmethod
    @session
    def add_user(
        email: str,
        name: str,
        protocol: Protocol,
        connection: EmailProtocol,
        session: Session,
    ) -> UserDTO:
        """
        Add a new user to the database.

        Args:
            email: Public email address (defaults to username if not provided)
            name: Optional display name
            protocol: Email protocol (default: IMAP)
            connection: The tested (-> valid) connection to the users server
            session: DB Session injected with @session

        Returns:
            UserDTO for the created user
        """
        existing = session.exec(select(User).where(User.email == email)).first()

        if existing:
            raise ValueError("User already exists.")

        user = User(name=name, email=email, protocol=protocol, connection=connection.serialize())
        session.add(user)
        session.commit()
        session.flush()
        session.refresh(user)
        return UserService.user_to_dto(user)

    @staticmethod
    @session
    def delete_user(user_id: int, session: Session) -> None:
        """
        Delete a user from the database by username.

        Args:
            user_id: Id of the user to delete
        """
        session.delete(session.get(User, user_id))
        # todo: handle keyring

    @staticmethod
    @session
    def get_all_users(session: Session) -> list[UserDTO]:
        """
        Get all users from the database as DTOs.

        Returns:
            List of all UserDTO objects
        """
        statement = select(User)
        results = session.exec(statement).all()
        return [UserService.user_to_dto(user) for user in results]

    @session
    def reload_all_user_mails(self, user_id: int, session: Session) -> None:
        user = session.get(User, user_id)
        if not user:
            return
        for conversation in user.conversations:
            session.delete(conversation)
