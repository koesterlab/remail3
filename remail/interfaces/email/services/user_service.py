"""User service for managing email account users."""

import logging

import keyring
from sqlmodel import Session, select
from werkzeug.security import generate_password_hash

from remail.controllers.dtos.user_dto import UserDTO
from remail.database.db import engine
from remail.enums import Protocol
from remail.models.user import User
from remail.utils.session_management import session

_KEYRING_SERVICE = "remail"
_REDACTED_VALUE = "<redacted>"
_logger = logging.getLogger(__name__)


class UserService:
    """Service for managing user accounts in the database."""

    @staticmethod
    def _ensure_user_schema() -> None:
        with engine.begin() as conn:
            result = conn.exec_driver_sql("PRAGMA table_info(users)")
            columns = [row[1] for row in result]
            if not columns:
                return
            if "username" not in columns and "email" in columns:
                conn.exec_driver_sql("ALTER TABLE users RENAME COLUMN email TO username")

    @staticmethod
    @session
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

        return UserDTO.get_from_model(user, UserService.count_unread(user))

    @staticmethod
    @session
    def get_user_by_id(user_id: int, session: Session) -> UserDTO | None:
        user = session.get(User, user_id)
        if not user:
            return None
        return UserService.user_to_dto(user)

    @staticmethod
    def get_user_by_username(username: str) -> User | None:
        """
        Get user by username.

        Args:
            username: Username to search for

        Returns:
            User object if found, None otherwise
        """
        UserService._ensure_user_schema()
        with Session(engine) as session:
            statement = select(User).where(User.username == username)
            return session.exec(statement).first()

    @staticmethod
    def get_user_by_email(email: str) -> User | None:
        """Backward-compatible alias for username lookup."""
        return UserService.get_user_by_username(email)

    @staticmethod
    def _is_hashed_password(value: str) -> bool:
        return value.startswith(("pbkdf2:", "scrypt:", "argon2:"))

    @staticmethod
    def get_user_password(username: str) -> str | None:
        """
        Retrieve the raw password from keyring. If the database still has a
        legacy plaintext password, migrate it to a hash.
        """
        UserService._ensure_user_schema()
        stored = keyring.get_password(_KEYRING_SERVICE, username)

        with Session(engine) as session:
            user = session.exec(select(User).where(User.username == username)).first()

            if user and user.password and not UserService._is_hashed_password(user.password):
                raw_password = stored or user.password

                if not stored:
                    try:
                        keyring.set_password(_KEYRING_SERVICE, username, raw_password)
                    except Exception as exc:
                        _logger.warning(
                            "Failed to store password in keyring for %s: %s", username, exc
                        )

                user.password = generate_password_hash(raw_password)
                session.add(user)
                session.commit()

                return raw_password

        return stored

    @staticmethod
    def add_user(
        username: str,
        password: str,
        host: str,
        email: str | None = None,
        name: str | None = None,
        protocol: Protocol = Protocol.IMAP,
    ) -> UserDTO:
        """
        Add a new user to the database.

        Args:
            username: Username
            password: Account password
            host: IMAP/SMTP host
            email: Public email address (defaults to username if not provided)
            name: Optional display name
            protocol: Email protocol (default: IMAP)

        Returns:
            UserDTO for the created user
        """
        UserService._ensure_user_schema()
        with Session(engine) as session:
            existing = session.exec(select(User).where(User.username == username)).first()

            if existing:
                raise ValueError("User already exists.")

            try:
                keyring.set_password(_KEYRING_SERVICE, username, password)
            except Exception as exc:
                raise RuntimeError("Failed to store password securely.") from exc

            resolved_name = name or username
            resolved_email = email or username
            if not resolved_email:
                raise ValueError("Email address is required.")

            user = User(
                name=resolved_name,
                email=resolved_email,
                username=username,
                host=host,
                password=generate_password_hash(password),
                protocol=protocol,
            )

            try:
                session.add(user)
                session.commit()
                session.refresh(user)
            except Exception:
                try:
                    keyring.delete_password(_KEYRING_SERVICE, username)
                except Exception as exc:
                    _logger.warning("Failed to rollback keyring password for %s: %s", username, exc)
                raise

            return UserService.user_to_dto(user)

    @staticmethod
    def delete_user(username: str) -> None:
        """
        Delete a user from the database by username.

        Args:
            username: Username to delete
        """
        UserService._ensure_user_schema()
        with Session(engine) as session:
            user = session.exec(select(User).where(User.username == username)).first()

            if not user:
                raise ValueError("User not found.")

            session.delete(user)
            session.commit()

        try:
            keyring.delete_password(_KEYRING_SERVICE, username)
        except Exception as exc:
            _logger.warning("Failed to delete keyring password for %s: %s", username, exc)

    @staticmethod
    def get_all_users() -> list[UserDTO]:
        """
        Get all users from the database as DTOs.

        Returns:
            List of all UserDTO objects
        """
        UserService._ensure_user_schema()
        with Session(engine) as session:
            statement = select(User)
            results = session.exec(statement).all()
            return [UserService.user_to_dto(user) for user in results]
