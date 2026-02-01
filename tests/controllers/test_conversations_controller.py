"""Tests for ConversationsController."""

from unittest.mock import MagicMock, patch

import pytest

from remail.controllers.conversations_controller import ConversationsController
from remail.controllers.dtos.conversations import ContactDTO, ConversationDTO
from remail.enums import ContactType


@pytest.fixture
def mock_conversation_service():
    """Create a mock ConversationService."""
    with patch("remail.controllers.conversations_controller.ConversationService") as mock:
        service_instance = MagicMock()
        mock.return_value = service_instance
        yield service_instance


@pytest.fixture
def mock_thread_service():
    """Create a mock ThreadService."""
    with patch("remail.controllers.conversations_controller.ThreadService") as mock:
        service_instance = MagicMock()
        service_instance.get_thread_for_conversation.return_value = None
        mock.return_value = service_instance
        yield service_instance


@pytest.fixture
def controller(mock_conversation_service, mock_thread_service):
    """Create a ConversationsController instance with mocked service."""
    return ConversationsController()


class TestConversationsController:
    """Test suite for ConversationsController."""

    def test_controller_initializes_with_service(self, controller, mock_conversation_service):
        """Test that controller initializes with ConversationService."""
        assert controller.service == mock_conversation_service

    def test_get_conversations_returns_list(self, controller, mock_conversation_service):
        """Test that get_conversations returns a list of ConversationDTO."""
        # Mock service response
        mock_conversation_service.get_all_conversations.return_value = []

        result = controller.get_conversations(user_id=1)

        assert isinstance(result, list)
        mock_conversation_service.get_all_conversations.assert_called_once_with(1)

    def test_get_conversations_calls_service_with_user_id(
        self, controller, mock_conversation_service
    ):
        """Test that get_conversations calls service with correct user_id."""
        mock_conversation_service.get_all_conversations.return_value = []

        controller.get_conversations(user_id=42)

        mock_conversation_service.get_all_conversations.assert_called_once_with(42)

    def test_get_conversations_converts_service_data_to_dtos(
        self, controller, mock_conversation_service
    ):
        """Test that get_conversations converts service data to DTOs."""
        # Mock service response matching actual service output
        service_data = [
            {
                "id": 1,
                "custom_name": "Test Conversation",
                "type": "conversation",
                "is_favorite": True,
                "contacts": [
                    {
                        "id": 10,
                        "email": "test@example.com",
                        "first_name": "John",
                        "last_name": "Doe",
                        "type": "private",
                        "is_known": True,
                    }
                ],
            }
        ]
        mock_conversation_service.get_all_conversations.return_value = service_data

        result = controller.get_conversations(user_id=1)

        assert len(result) == 1
        assert isinstance(result[0], ConversationDTO)
        assert result[0].custom_name == "Test Conversation"
        assert result[0].is_favorite is True
        assert result[0].threads == []

    def test_get_conversations_converts_multiple_conversations(
        self, controller, mock_conversation_service
    ):
        """Test that get_conversations converts multiple conversations."""
        # Mock service response with multiple conversations
        service_data = [
            {
                "id": 1,
                "custom_name": "First",
                "type": "conversation",
                "is_favorite": True,
                "contacts": [],
            },
            {
                "id": 2,
                "custom_name": "Second",
                "type": "group",
                "is_favorite": False,
                "contacts": [],
            },
            {
                "id": 3,
                "custom_name": "Third",
                "type": "conversation",
                "is_favorite": True,
                "contacts": [],
            },
        ]
        mock_conversation_service.get_all_conversations.return_value = service_data

        result = controller.get_conversations(user_id=1)

        assert len(result) == 3
        assert all(isinstance(conv, ConversationDTO) for conv in result)
        assert result[0].custom_name == "First"
        assert result[1].custom_name == "Second"
        assert result[2].custom_name == "Third"

    def test_get_conversations_converts_contacts_to_dtos(
        self, controller, mock_conversation_service
    ):
        """Test that get_conversations converts contacts to ContactDTO."""
        # Mock service response with contacts
        service_data = [
            {
                "id": 1,
                "custom_name": "Test",
                "type": "conversation",
                "is_favorite": False,
                "contacts": [
                    {
                        "id": 10,
                        "email": "contact1@example.com",
                        "first_name": "Alice",
                        "last_name": "Johnson",
                        "type": "private",
                        "is_known": True,
                    },
                    {
                        "id": 20,
                        "email": "contact2@example.com",
                        "first_name": "Bob",
                        "last_name": "Smith",
                        "type": "private",
                        "is_known": False,
                    },
                ],
            }
        ]
        mock_conversation_service.get_all_conversations.return_value = service_data

        result = controller.get_conversations(user_id=1)

        assert len(result) == 1
        assert len(result[0].contacts) == 2
        assert all(isinstance(contact, ContactDTO) for contact in result[0].contacts)
        assert result[0].contacts[0].email == "contact1@example.com"
        assert result[0].contacts[0].type == ContactType.PRIVATE
        assert result[0].contacts[1].email == "contact2@example.com"
        assert result[0].contacts[1].type == ContactType.PRIVATE

    def test_get_conversations_handles_empty_list(self, controller, mock_conversation_service):
        """Test that get_conversations handles empty list from service."""
        mock_conversation_service.get_all_conversations.return_value = []

        result = controller.get_conversations(user_id=1)

        assert result == []
        assert isinstance(result, list)

    def test_get_conversations_preserves_conversation_types(
        self, controller, mock_conversation_service
    ):
        """Test that conversation types are correctly converted."""
        service_data = [
            {
                "id": 1,
                "custom_name": "Regular",
                "type": "conversation",
                "is_favorite": False,
                "contacts": [],
            },
            {
                "id": 2,
                "custom_name": "Group",
                "type": "group",
                "is_favorite": False,
                "contacts": [],
            },
        ]
        mock_conversation_service.get_all_conversations.return_value = service_data

        result = controller.get_conversations(user_id=1)

        # Note: New DTO doesn't have a 'type' field, only customName
        assert result[0].custom_name == "Regular"
        assert result[1].custom_name == "Group"

    def test_get_conversations_preserves_favorite_status(
        self, controller, mock_conversation_service
    ):
        """Test that favorite status is preserved."""
        service_data = [
            {
                "id": 1,
                "custom_name": "Favorite",
                "type": "conversation",
                "is_favorite": True,
                "contacts": [],
            },
            {
                "id": 2,
                "custom_name": "Not Favorite",
                "type": "conversation",
                "is_favorite": False,
                "contacts": [],
            },
        ]
        mock_conversation_service.get_all_conversations.return_value = service_data

        result = controller.get_conversations(user_id=1)

        assert result[0].is_favorite is True
        assert result[1].is_favorite is False

    def test_get_conversations_with_group_conversation(self, controller, mock_conversation_service):
        """Test get_conversations with a group conversation containing multiple contacts."""
        service_data = [
            {
                "id": 1,
                "custom_name": "Team Discussion",
                "type": "group",
                "is_favorite": True,
                "contacts": [
                    {
                        "id": 1,
                        "email": "alice@example.com",
                        "first_name": "Alice",
                        "last_name": "Wonder",
                        "type": "private",
                        "is_known": True,
                    },
                    {
                        "id": 2,
                        "email": "bob@example.com",
                        "first_name": "Bob",
                        "last_name": "Builder",
                        "type": "private",
                        "is_known": True,
                    },
                    {
                        "id": 3,
                        "email": "charlie@example.com",
                        "first_name": "Charlie",
                        "last_name": "Brown",
                        "type": "private",
                        "is_known": False,
                    },
                ],
            }
        ]
        mock_conversation_service.get_all_conversations.return_value = service_data
        result = controller.get_conversations(user_id=1)

        assert len(result) == 1
        assert len(result[0].contacts) == 3
        assert result[0].contacts[0].first_name == "Alice"
        assert result[0].contacts[1].first_name == "Bob"
        assert result[0].contacts[2].first_name == "Charlie"
