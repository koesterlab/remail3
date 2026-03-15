"""Tests for UserService."""

from unittest.mock import Mock

import pytest
from sqlmodel import Session

from remail.enums import Protocol
from remail.interfaces.email.services.user_service import UserService
from remail.models import User, Conversation, Thread


class TestUserService:
    """Test suite for UserService."""

    def test_get_user_by_email_found(self, test_engine):
        """Test getting user by email when user exists."""
        with Session(test_engine) as session:
            user = User(
                name="found",
                email="found@example.com",
                protocol=Protocol.IMAP,
                connection='{"host": "imap.example.com"}',
            )
            session.add(user)
            session.commit()
            session.refresh(user)

        found_user = UserService.get_user_by_email("found@example.com")

        assert found_user is not None
        assert found_user.email == "found@example.com"
        assert found_user.id == user.id

    def test_get_user_by_email_not_found(self):
        """Test getting user by email when user doesn't exist."""
        found_user = UserService.get_user_by_email("notfound@example.com")

        assert found_user is None

    def test_get_user_by_id_found(self, test_engine):
        """Test getting user by ID when user exists."""
        with Session(test_engine) as session:
            user = User(
                name="found_id",
                email="found_id@example.com",
                protocol=Protocol.IMAP,
                connection='{"host": "imap.example.com"}',
            )
            session.add(user)
            session.commit()
            session.refresh(user)
            user_id = user.id

        found_user = UserService.get_user_by_id(user_id)

        assert found_user is not None
        assert found_user.id == user_id
        assert found_user.email == "found_id@example.com"

    def test_get_user_by_id_not_found(self):
        """Test getting user by ID when user doesn't exist."""
        found_user = UserService.get_user_by_id(99999)

        assert found_user is None

    def test_get_all_users_empty(self):
        """Test getting all users when database is empty."""
        users = UserService.get_all_users()

        assert isinstance(users, list)
        assert len(users) == 0

    def test_get_all_users_multiple(self, test_engine):
        """Test getting all users when multiple exist."""
        with Session(test_engine) as session:
            session.add_all(
                [
                    User(
                        name="user1",
                        email="user1@example.com",
                        protocol=Protocol.IMAP,
                        connection='{"host": "imap.example.com"}',
                    ),
                    User(
                        name="user2",
                        email="user2@example.com",
                        protocol=Protocol.IMAP,
                        connection='{"host": "imap.example.com"}',
                    ),
                    User(
                        name="user3",
                        email="user3@example.com",
                        protocol=Protocol.IMAP,
                        connection='{"host": "imap.example.com"}',
                    ),
                ]
            )
            session.commit()

        users = UserService.get_all_users()

        assert len(users) == 3
        emails = {u.email for u in users}
        assert emails == {"user1@example.com", "user2@example.com", "user3@example.com"}

    def test_add_user_success(self, test_engine):
        """Test successfully adding a new user."""
        mock_protocol = Mock()
        mock_protocol.serialize.return_value = '{"host": "imap.test.com", "port": 993}'

        dto = UserService.add_user(
            email="new@example.com",
            name="New User",
            protocol=Protocol.IMAP,
            connection=mock_protocol,
        )

        assert dto is not None
        assert dto.email == "new@example.com"
        assert dto.name == "New User"
        mock_protocol.serialize.assert_called_once()

        # Verify user was actually saved
        saved_user = UserService.get_user_by_email("new@example.com")
        assert saved_user is not None
        assert saved_user.email == "new@example.com"

    def test_add_user_duplicate_raises_error(self, test_engine):
        """Test that adding duplicate user raises ValueError."""
        mock_protocol = Mock()
        mock_protocol.serialize.return_value = '{"host": "imap.test.com"}'

        UserService.add_user(
            email="duplicate@example.com",
            name="First",
            protocol=Protocol.IMAP,
            connection=mock_protocol,
        )

        with pytest.raises(ValueError, match="User already exists"):
            UserService.add_user(
                email="duplicate@example.com",
                name="Second",
                protocol=Protocol.IMAP,
                connection=mock_protocol,
            )

    def test_delete_user(self, test_engine):
        """Test deleting a user."""
        with Session(test_engine) as session:
            user = User(
                name="to_delete",
                email="delete@example.com",
                protocol=Protocol.IMAP,
                connection='{"host": "imap.example.com"}',
            )
            session.add(user)
            session.commit()
            session.refresh(user)
            user_id = user.id

        UserService.delete_user(user_id)

        # Verify user was deleted
        deleted_user = UserService.get_user_by_id(user_id)
        assert deleted_user is None

    def test_user_to_dto_requires_id(self):
        """Test user_to_dto raises when user has no id."""
        user = User(
            name="noid",
            email="noid@example.com",
            protocol=Protocol.IMAP,
            connection='{"host": "imap.example.com"}',
        )

        with pytest.raises(ValueError, match="User must have an ID"):
            UserService.user_to_dto(user)

    def test_user_to_dto_fields(self, test_engine):
        """Test user_to_dto maps fields correctly."""
        with Session(test_engine) as session:
            user = User(
                name="dto",
                email="dto@example.com",
                protocol=Protocol.IMAP,
                connection='{"host": "imap.example.com", "port": 993}',
            )
            session.add(user)
            session.commit()
            session.refresh(user)

        dto = UserService.user_to_dto(user)

        assert dto.id == user.id
        assert dto.name == "dto"
        assert dto.email == "dto@example.com"
        assert dto.unread_count == 0

    def test_count_unread_returns_zero(self, test_engine):
        """Test count_unread returns 0 when no unread threads."""
        with Session(test_engine) as session:
            user = User(
                name="cnt",
                email="cnt@example.com",
                protocol=Protocol.IMAP,
                connection='{"host": "imap.example.com"}',
            )
            session.add(user)
            session.commit()
            session.refresh(user)

        assert UserService.count_unread(user) == 0

    def test_count_unread_counts_threads_with_unread(self, test_engine):
        """Test count_unread correctly counts threads with unread messages."""
        with Session(test_engine) as session:
            user = User(
                name="unread_test",
                email="unread@example.com",
                protocol=Protocol.IMAP,
                connection='{"host": "imap.example.com"}',
            )
            session.add(user)
            session.flush()

            conv1 = Conversation(type="conversation", user=user)
            conv2 = Conversation(type="conversation", user=user)
            session.add_all([conv1, conv2])
            session.flush()

            thread1 = Thread(title="Thread 1", conversation=conv1, unread_count=5)
            thread2 = Thread(title="Thread 2", conversation=conv1, unread_count=0)
            thread3 = Thread(title="Thread 3", conversation=conv2, unread_count=3)
            session.add_all([thread1, thread2, thread3])
            session.commit()
            session.refresh(user)

        assert UserService.count_unread(user) == 2  # thread1 and thread3 have unread
