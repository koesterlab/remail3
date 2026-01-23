"""Tests for ContactsController."""

from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest

from remail.controllers.contacts_controller import ContactsController
from remail.controllers.dtos.conversations import ContactDTO
from remail.enums import ContactType


@pytest.fixture
def mock_contact_service():
    """Create a mock ContactService."""
    with patch("remail.controllers.contacts_controller.ContactService") as mock:
        service_instance = MagicMock()
        mock.return_value = service_instance
        yield service_instance


@pytest.fixture
def mock_conversation_service():
    """Create a mock ConversationService."""
    with patch("remail.controllers.contacts_controller.ConversationService") as mock:
        service_instance = MagicMock()
        mock.return_value = service_instance
        yield service_instance


@pytest.fixture
def controller(mock_contact_service, mock_conversation_service):
    """Create a ContactsController instance with mocked services."""
    return ContactsController()


class TestContactsController:
    """Test suite for ContactsController."""

    def test_controller_initializes_with_services(
        self, controller, mock_contact_service, mock_conversation_service
    ):
        """Test that controller initializes with services."""
        assert controller.service == mock_contact_service
        assert controller.conversation_service == mock_conversation_service

    def test_get_all_contacts_returns_dtos(self, controller, mock_contact_service):
        """Test that get_all_contacts returns ContactDTOs."""
        mock_contact_service.get_all_contacts.return_value = [
            SimpleNamespace(
                id=1,
                first_name="Alice",
                last_name="Smith",
                email_address="alice@example.com",
                is_known=True,
                contact_type=ContactType.PRIVATE,
            ),
            SimpleNamespace(
                id=2,
                first_name="Bob",
                last_name="Jones",
                email_address="bob@example.com",
                is_known=False,
                contact_type=ContactType.BUSINESS,
            ),
        ]

        result = controller.get_all_contacts(user_id=42)

        assert isinstance(result, list)
        assert len(result) == 2
        assert all(isinstance(contact, ContactDTO) for contact in result)
        assert result[0].email == "alice@example.com"
        assert result[1].type == ContactType.BUSINESS
        mock_contact_service.get_all_contacts.assert_called_once_with(42)

    def test_create_contact_calls_services_and_returns_dto(
        self, controller, mock_contact_service, mock_conversation_service
    ):
        """Test create_contact returns DTO and creates conversation."""
        contact = SimpleNamespace(
            id=5,
            first_name="Bob",
            last_name="Builder",
            email_address="bob@example.com",
            is_known=False,
            contact_type=ContactType.BUSINESS,
        )
        mock_contact_service.create_contact.return_value = contact

        result = controller.create_contact(
            user_id=7,
            email="bob@example.com",
            first_name="Bob",
            last_name="Builder",
            contact_type="business",
        )

        assert isinstance(result, ContactDTO)
        assert result.id == 5
        assert result.is_known is False
        assert result.type == ContactType.BUSINESS
        mock_contact_service.create_contact.assert_called_once_with(
            email="bob@example.com",
            first_name="Bob",
            last_name="Builder",
            contact_type=ContactType.BUSINESS,
            is_known=True,
            name=None,
        )
        mock_conversation_service.create_conversation.assert_called_once_with(
            user_id=7,
            contact_ids=[5],
        )

    def test_create_contact_returns_none_when_service_returns_none(
        self, controller, mock_contact_service, mock_conversation_service
    ):
        """Test create_contact returns None when service returns None."""
        mock_contact_service.create_contact.return_value = None

        result = controller.create_contact(
            user_id=3,
            email="missing@example.com",
        )

        assert result is None
        mock_conversation_service.create_conversation.assert_not_called()
