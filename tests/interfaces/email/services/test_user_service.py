"""Tests for UserService."""

import pytest
from sqlmodel import Session

from remail.enums import Protocol, UserAccountCategory
from remail.interfaces.email.services.user_service import UserService
from remail.models import User


class TestUserService:
    """Test suite for UserService."""

    def test_get_user_by_email_found(self, test_engine):
        """Test getting user by username when user exists."""
        with Session(test_engine) as session:
            user = User(
                name="found",
                username="found@example.com",
                host="imap.example.com",
                password="hash123",
                protocol=Protocol.IMAP,
            )
            session.add(user)
            session.commit()
            session.refresh(user)

        found_user = UserService.get_user_by_email("found@example.com")

        assert found_user is not None
        assert found_user.username == "found@example.com"
        assert found_user.id == user.id

    def test_get_user_by_email_not_found(self):
        """Test getting user by email when user doesn't exist."""
        found_user = UserService.get_user_by_email("notfound@example.com")

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
                        username="user1@example.com",
                        host="imap.example.com",
                        password="hash1",
                        protocol=Protocol.IMAP,
                    ),
                    User(
                        name="user2",
                        username="user2@example.com",
                        host="imap.example.com",
                        password="hash2",
                        protocol=Protocol.IMAP,
                    ),
                    User(
                        name="user3",
                        username="user3@example.com",
                        host="imap.example.com",
                        password="hash3",
                        protocol=Protocol.IMAP,
                    ),
                ]
            )
            session.commit()

        users = UserService.get_all_users()

        assert len(users) == 3
        usernames = {u.username for u in users}
        assert usernames == {"user1@example.com", "user2@example.com", "user3@example.com"}
        assert all(u.host == "imap.example.com" for u in users)
        assert all(u.category == UserAccountCategory.PRIVATE for u in users)

    def test_user_to_dto_requires_id(self):
        """Test user_to_dto raises when user has no id."""
        user = User(
            name="noid",
            username="noid@example.com",
            host="imap.example.com",
            password="hash",
            protocol=Protocol.IMAP,
        )

        with pytest.raises(ValueError, match="User must have an ID"):
            UserService.user_to_dto(user)

    def test_user_to_dto_fields(self, test_engine):
        """Test user_to_dto maps fields correctly."""
        with Session(test_engine) as session:
            user = User(
                name="dto",
                username="dto@example.com",
                host="imap.example.com",
                password="hash",
                protocol=Protocol.IMAP,
            )
            session.add(user)
            session.commit()
            session.refresh(user)

        dto = UserService.user_to_dto(user)

        assert dto.id == user.id
        assert dto.name == "dto"
        assert dto.username == "dto@example.com"
        assert dto.host == "imap.example.com"
        assert dto.password != user.password
        assert dto.protocol == Protocol.IMAP
        assert dto.category == UserAccountCategory.PRIVATE
        assert dto.unread_conversations == 0

    def test_count_unread_returns_zero(self, test_engine):
        """Test count_unread returns default 0."""
        with Session(test_engine) as session:
            user = User(
                name="cnt",
                username="cnt@example.com",
                host="imap.example.com",
                password="hash",
                protocol=Protocol.IMAP,
            )
            session.add(user)
            session.commit()
            session.refresh(user)

        assert UserService.count_unread(user) == 0
