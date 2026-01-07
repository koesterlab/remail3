"""Tests for UserService."""

from unittest.mock import patch

import pytest
from sqlalchemy.pool import StaticPool
from sqlmodel import SQLModel, create_engine

from remail.enums import Protocol
from remail.interfaces.email.services.user_service import UserService


class TestUserService:
    """Test suite for UserService."""

    @pytest.fixture
    def test_engine(self):
        """Create a fresh test database engine for each test."""
        import os

        # Use test.db file and clean it up after each test
        test_db_path = "test.db"
        # Remove test.db if it exists from previous test
        if os.path.exists(test_db_path):
            os.remove(test_db_path)

        engine = create_engine(
            f"sqlite:///{test_db_path}",
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
            echo=False,
        )
        SQLModel.metadata.create_all(engine)
        yield engine
        SQLModel.metadata.drop_all(engine)
        # Clean up test database file
        if os.path.exists(test_db_path):
            os.remove(test_db_path)

    @pytest.fixture(autouse=True)
    def setup_database(self, test_engine):
        """Auto-patch the database engine for all tests."""
        with patch("remail.database.db.engine", test_engine):
            with patch("remail.interfaces.email.services.user_service.engine", test_engine):
                yield

    def test_add_user_success(self):
        """Test adding a new user successfully."""
        user = UserService.add_user(
            email="test@example.com",
            password="hashed_password",
        )

        assert user is not None
        assert user.email == "test@example.com"
        assert user.password == "hashed_password"
        assert user.name == "test"  # Extracted from email
        assert user.protocol == Protocol.IMAP  # Default protocol
        assert user.id is not None

    def test_add_user_with_name(self):
        """Test adding user with explicit name."""
        user = UserService.add_user(
            email="john@example.com",
            password="hash123",
            name="John Doe",
        )

        assert user.name == "John Doe"
        assert user.email == "john@example.com"

    def test_add_user_with_protocol(self):
        """Test adding user with explicit protocol."""
        user = UserService.add_user(
            email="exchange@example.com",
            password="hash123",
            protocol=Protocol.EXCHANGE,
        )

        assert user.protocol == Protocol.EXCHANGE

    def test_add_user_duplicate_email_raises_valueerror(self):
        """Test that adding duplicate email raises ValueError."""
        # Add first user
        UserService.add_user(email="duplicate@example.com", password="hash1")

        # Try to add duplicate
        with pytest.raises(ValueError, match="already exists"):
            UserService.add_user(email="duplicate@example.com", password="hash2")

    def test_get_user_by_email_found(self):
        """Test getting user by email when user exists."""
        # Create user
        created_user = UserService.add_user(email="found@example.com", password="hash123")

        # Get user
        found_user = UserService.get_user_by_email("found@example.com")

        assert found_user is not None
        assert found_user.email == "found@example.com"
        assert found_user.id == created_user.id

    def test_get_user_by_email_not_found(self):
        """Test getting user by email when user doesn't exist."""
        found_user = UserService.get_user_by_email("notfound@example.com")

        assert found_user is None

    def test_get_user_by_id_found(self):
        """Test getting user by ID when user exists."""
        # Create user
        created_user = UserService.add_user(email="found@example.com", password="hash123")

        # Get user by ID
        found_user = UserService.get_user_by_id(created_user.id)

        assert found_user is not None
        assert found_user.id == created_user.id
        assert found_user.email == "found@example.com"

    def test_get_user_by_id_not_found(self):
        """Test getting user by ID when user doesn't exist."""
        found_user = UserService.get_user_by_id(99999)

        assert found_user is None

    def test_get_all_users_empty(self):
        """Test getting all users when database is empty."""
        users = UserService.get_all_users()

        assert isinstance(users, list)
        assert len(users) == 0

    def test_get_all_users_multiple(self):
        """Test getting all users when multiple exist."""
        # Create multiple users
        UserService.add_user(email="user1@example.com", password="hash1")
        UserService.add_user(email="user2@example.com", password="hash2")
        UserService.add_user(email="user3@example.com", password="hash3")

        users = UserService.get_all_users()

        assert len(users) == 3
        emails = [u.email for u in users]
        assert "user1@example.com" in emails
        assert "user2@example.com" in emails
        assert "user3@example.com" in emails

    def test_update_user_all_fields(self):
        """Test updating all user fields."""
        # Create user
        user = UserService.add_user(
            email="original@example.com",
            password="old_password",
            name="Original Name",
            protocol=Protocol.IMAP,
        )

        # Update all fields
        updated_user = UserService.update_user(
            user_id=user.id,
            name="New Name",
            email="new@example.com",
            password="new_password",
            protocol=Protocol.EXCHANGE,
        )

        assert updated_user is not None
        assert updated_user.name == "New Name"
        assert updated_user.email == "new@example.com"
        assert updated_user.password == "new_password"
        assert updated_user.protocol == Protocol.EXCHANGE

    def test_update_user_partial_fields(self):
        """Test updating only some user fields."""
        # Create user
        user = UserService.add_user(
            email="partial@example.com",
            password="old_password",
            name="Old Name",
            protocol=Protocol.IMAP,
        )

        # Update only name
        updated_user = UserService.update_user(user_id=user.id, name="New Name")

        assert updated_user is not None
        assert updated_user.name == "New Name"
        assert updated_user.email == "partial@example.com"  # Unchanged
        assert updated_user.password == "old_password"  # Unchanged
        assert updated_user.protocol == Protocol.IMAP  # Unchanged

    def test_update_user_not_found(self):
        """Test updating user that doesn't exist."""
        updated_user = UserService.update_user(user_id=99999, name="New Name")

        assert updated_user is None

    def test_update_user_duplicate_email_raises_valueerror(self):
        """Test that updating email to existing one raises ValueError."""
        # Create two users
        UserService.add_user(email="user1@example.com", password="hash1")
        user2 = UserService.add_user(email="user2@example.com", password="hash2")

        # Try to change user2's email to user1's email
        with pytest.raises(ValueError, match="already taken"):
            UserService.update_user(user_id=user2.id, email="user1@example.com")

    def test_update_user_same_email_allowed(self):
        """Test that updating to the same email is allowed."""
        user = UserService.add_user(email="same@example.com", password="hash1")

        # Update with same email should work
        updated_user = UserService.update_user(user_id=user.id, email="same@example.com")

        assert updated_user is not None
        assert updated_user.email == "same@example.com"

    def test_delete_user_success(self):
        """Test successful user deletion by email."""
        # Create user
        UserService.add_user(email="delete@example.com", password="hash123")

        # Delete user
        result = UserService.delete_user("delete@example.com")

        assert result is True

        # Verify user is gone
        found_user = UserService.get_user_by_email("delete@example.com")
        assert found_user is None

    def test_delete_user_not_found(self):
        """Test deleting user that doesn't exist."""
        result = UserService.delete_user("nonexistent@example.com")

        assert result is False

    def test_delete_user_by_id_success(self):
        """Test successful user deletion by ID."""
        # Create user
        user = UserService.add_user(email="deleteid@example.com", password="hash123")

        # Delete user
        result = UserService.delete_user_by_id(user.id)

        assert result is True

        # Verify user is gone
        found_user = UserService.get_user_by_id(user.id)
        assert found_user is None

    def test_delete_user_by_id_not_found(self):
        """Test deleting user by ID that doesn't exist."""
        result = UserService.delete_user_by_id(99999)

        assert result is False
