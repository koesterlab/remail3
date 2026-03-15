"""Tests for ContactService."""

import pytest
from sqlmodel import Session

from remail.enums import Protocol
from remail.interfaces.email.services.contact_service import ContactService
from remail.models import Contact, User


class TestContactService:
    """Test suite for ContactService."""

    def test_get_contact_by_id_found(self, test_engine):
        """Test get_contact_by_id returns contact when found."""
        with Session(test_engine) as session:
            contact = Contact(
                name="John Doe",
                email_address="john@example.com",
                first_name="John",
                last_name="Doe",
                is_known=True,
            )
            session.add(contact)
            session.commit()
            session.refresh(contact)
            contact_id = contact.id

        service = ContactService()
        result = service.get_contact_by_id(contact_id)

        assert result is not None
        assert result.id == contact_id
        assert result.name == "John Doe"
        assert result.email_address == "john@example.com"

    def test_get_contact_by_id_not_found(self):
        """Test get_contact_by_id returns None when not found."""
        service = ContactService()
        result = service.get_contact_by_id(99999)

        assert result is None

    def test_get_or_create_contact_creates_new(self, test_engine):
        """Test get_or_create_contact creates new contact when not exists."""
        service = ContactService()
        result = service.get_or_create_contact(
            email="new@example.com",
            name="New User"
        )

        assert result is not None
        assert result.email_address == "new@example.com"
        assert result.name == "New User"
        assert result.is_known is False

        # Verify contact was saved
        with Session(test_engine) as session:
            from sqlmodel import select
            saved = session.exec(
                select(Contact).where(Contact.email_address == "new@example.com")
            ).first()
            assert saved is not None
            assert saved.name == "New User"

    def test_get_or_create_contact_returns_existing(self, test_engine):
        """Test get_or_create_contact returns existing contact."""
        with Session(test_engine) as session:
            existing = Contact(
                name="Existing User",
                email_address="existing@example.com",
                is_known=True,
            )
            session.add(existing)
            session.commit()
            session.refresh(existing)
            existing_id = existing.id

        service = ContactService()
        result = service.get_or_create_contact(
            email="existing@example.com",
            name="Different Name"
        )

        # Should return existing contact, not create new one
        assert result.id == existing_id
        assert result.name == "Existing User"  # Original name preserved
        assert result.email_address == "existing@example.com"

    def test_get_or_create_contact_uses_email_as_name_fallback(self, test_engine):
        """Test get_or_create_contact uses email as name when name not provided."""
        service = ContactService()
        result = service.get_or_create_contact(email="test@example.com")

        assert result.name == "test@example.com"
        assert result.email_address == "test@example.com"

    def test_get_or_create_contact_raises_on_empty_email(self):
        """Test get_or_create_contact raises ValueError for empty email."""
        service = ContactService()

        with pytest.raises(ValueError, match="Contact email is required"):
            service.get_or_create_contact(email="")

    def test_get_or_create_contact_raises_on_none_email(self):
        """Test get_or_create_contact raises ValueError for None email."""
        service = ContactService()

        with pytest.raises(ValueError, match="Contact email is required"):
            service.get_or_create_contact(email=None)

    def test_get_user_contact(self, test_engine):
        """Test get_user_contact creates/returns contact for user."""
        with Session(test_engine) as session:
            user = User(
                name="Test User",
                email="user@example.com",
                protocol=Protocol.IMAP,
                connection='{"host": "imap.example.com"}',
            )
            session.add(user)
            session.commit()
            session.refresh(user)

        service = ContactService()
        result = service.get_user_contact(user)

        assert result is not None
        assert result.email_address == "user@example.com"
        assert result.name == "Test User"

    def test_get_user_contact_idempotent(self, test_engine):
        """Test get_user_contact returns same contact on multiple calls."""
        with Session(test_engine) as session:
            user = User(
                name="Repeat User",
                email="repeat@example.com",
                protocol=Protocol.IMAP,
                connection='{"host": "imap.example.com"}',
            )
            session.add(user)
            session.commit()
            session.refresh(user)

        service = ContactService()
        result1 = service.get_user_contact(user)
        result2 = service.get_user_contact(user)

        # Should return same contact
        assert result1.id == result2.id
        assert result1.email_address == result2.email_address

    def test_get_or_create_contact_case_sensitive_email(self, test_engine):
        """Test get_or_create_contact treats emails case-sensitively."""
        service = ContactService()

        contact1 = service.get_or_create_contact(
            email="test@example.com",
            name="Lowercase"
        )
        contact2 = service.get_or_create_contact(
            email="TEST@example.com",
            name="Uppercase"
        )

        # Depending on DB collation, these might be same or different
        # Most email systems treat emails as case-insensitive
        # But this test documents current behavior
        assert contact1.email_address == "test@example.com"
        assert contact2.email_address == "TEST@example.com"

    def test_get_or_create_contact_trims_whitespace(self, test_engine):
        """Test get_or_create_contact handles emails with whitespace."""
        service = ContactService()

        # This documents current behavior - service doesn't trim
        # If this test fails, it means trimming was added
        result = service.get_or_create_contact(
            email=" whitespace@example.com ",
            name="Whitespace Test"
        )

        # Current behavior: whitespace preserved
        assert result.email_address == " whitespace@example.com "
