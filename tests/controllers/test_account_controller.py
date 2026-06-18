"""Tests for AccountController."""

from collections.abc import Iterable
from unittest.mock import AsyncMock, Mock, patch

import pytest

from remail.controllers.account_controller import AccountController
from remail.controllers.dtos.conversations import ContactDTO, ConversationDTO
from remail.controllers.dtos.user_dto import UserDTO
from remail.enums import Protocol
from remail.models import Contact, Conversation, User


@pytest.fixture
def mock_services():
    """Mock all service dependencies."""
    with (
        patch("remail.controllers.account_controller.UserService") as mock_user_service,
        patch("remail.controllers.account_controller.EmailSyncService") as mock_sync_service,
        patch("remail.controllers.account_controller.ThreadService") as mock_thread_service,
        patch("remail.controllers.account_controller.ConversationService") as mock_conv_service,
        patch("remail.controllers.account_controller.ContactService") as mock_contact_service,
    ):
        # Setup UserService
        user_instance = mock_user_service.return_value
        mock_user = Mock(spec=User)
        mock_user.id = 1
        mock_user.email = "test@example.com"
        mock_user.name = "Test User"
        mock_user.conversations = []

        mock_user_service.get_user_by_id.return_value = mock_user
        user_instance.get_user_by_id.return_value = mock_user
        mock_user_service.count_unread.return_value = 0

        yield {
            "user_service": mock_user_service,
            "user_instance": user_instance,
            "sync_service": mock_sync_service.return_value,
            "thread_service": mock_thread_service.return_value,
            "conv_service": mock_conv_service.return_value,
            "contact_service": mock_contact_service.return_value,
            "mock_user": mock_user,
        }


class TestAccountControllerStaticMethods:
    """Test suite for static methods."""

    def test_all_client_accounts(self):
        """Test all_client_accounts returns list of AccountControllers."""
        mock_user_dto = UserDTO(id=1, email="test@example.com", name="Test", unread_count=0)

        with patch("remail.controllers.account_controller.UserService") as mock_service:
            mock_service.return_value.get_all_users.return_value = [mock_user_dto]

            with patch.object(AccountController, "__init__", lambda self, account_id: None):
                result = AccountController.all_client_accounts()

                assert len(result) == 1
                assert isinstance(result[0], AccountController)

    def test_create_new_account_success(self):
        """Test create_new_account with valid credentials."""
        mock_protocol = Mock()
        mock_protocol.test_connection.return_value = True

        with patch("remail.controllers.account_controller.UserService") as mock_service:
            AccountController.create_new_account(
                clearname="John Doe",
                email="john@example.com",
                connection=mock_protocol,
                method=Protocol.IMAP,
            )

            mock_protocol.test_connection.assert_called_once()
            mock_service.return_value.add_user.assert_called_once_with(
                "john@example.com", "John Doe", Protocol.IMAP, mock_protocol
            )

    def test_create_new_account_invalid_credentials(self):
        """Test create_new_account with invalid credentials raises ValueError."""
        mock_protocol = Mock()
        mock_protocol.test_connection.return_value = False

        with pytest.raises(ValueError, match="Creating account with invalid credentials"):
            AccountController.create_new_account(
                clearname="John Doe",
                email="john@example.com",
                connection=mock_protocol,
                method=Protocol.IMAP,
            )


class TestAccountControllerInit:
    """Test suite for initialization."""

    def test_init_sets_user_data(self, mock_services):
        """Test initialization sets user data correctly."""
        controller = AccountController(account_id=1)

        assert controller.user_id == 1
        assert isinstance(controller.user, UserDTO)
        assert controller.user.email == "test@example.com"


class TestAccountControllerConversations:
    """Test suite for conversation-related methods."""

    def test_get_conversations(self, mock_services):
        """Test get_conversations syncs and returns conversations."""
        controller = AccountController(account_id=1)

        with patch.object(controller, "_get_conversations_from_db", return_value=[]):
            result = controller.get_conversations()

        mock_services["sync_service"].sync_emails.assert_called_once()
        assert isinstance(result, list)

    def test_create_conversation(self, mock_services):
        """Test create_conversation creates and returns ConversationDTO."""
        mock_conversation = Mock(spec=Conversation)
        mock_conversation.id = 1
        mock_conversation.is_favorite = False
        mock_conversation.custom_name = "Test Conversation"
        mock_conversation.contacts = []
        mock_conversation.threads = []

        mock_contact = Mock(spec=Contact)
        mock_contact.id = 1

        mock_services["conv_service"].create_conversation.return_value = mock_conversation
        mock_services["contact_service"].get_contact_by_id.return_value = mock_contact

        controller = AccountController(account_id=1)
        contact_dto = ContactDTO(
            id=1,
            first_name="Jane",
            last_name="Doe",
            email="jane@example.com",
            is_known=True,
            type="TO",
        )

        result = controller.create_conversation(contacts=[contact_dto])

        assert isinstance(result, ConversationDTO)
        mock_services["conv_service"].create_conversation.assert_called_once()


class TestAccountControllerCallbacks:
    """Test suite for callback methods."""

    def test_set_callback_email_changes(self, mock_services):
        """Test set_callback_email_changes registers callback."""
        controller = AccountController(account_id=1)
        callback_called = False

        def test_callback(conversations: Iterable[ConversationDTO]):
            nonlocal callback_called
            callback_called = True

        controller.set_callback_email_changes(test_callback)
        assert controller.callback == test_callback

    def test_set_callback_email_errors(self, mock_services):
        """Test set_callback_email_errors registers error callback."""
        controller = AccountController(account_id=1)
        error_msg = None

        def test_error_callback(msg: str):
            nonlocal error_msg
            error_msg = msg

        controller.set_callback_email_errors(test_error_callback)
        controller._notify_error("Test error")

        assert error_msg == "Test error"


class TestAccountControllerGetters:
    """Test suite for getter methods."""

    def test_get_email_address(self, mock_services):
        """Test get_email_address returns user email."""
        controller = AccountController(account_id=1)
        assert controller.get_email_address() == "test@example.com"

    def test_get_plain_name(self, mock_services):
        """Test get_plain_name returns user name."""
        controller = AccountController(account_id=1)
        assert controller.get_plain_name() == "Test User"

    def test_get_user(self, mock_services):
        """Test get_user returns UserDTO."""
        controller = AccountController(account_id=1)
        user = controller.get_user()

        assert isinstance(user, UserDTO)
        assert user.email == "test@example.com"


class TestAccountControllerDelete:
    """Test suite for delete operations."""

    def test_delete(self, mock_services):
        """Test delete calls UserService.delete_user."""
        controller = AccountController(account_id=1)

        with patch.object(mock_services["user_service"], "delete_user") as mock_delete:
            controller.delete()
            mock_delete.assert_called_once_with(1)


class TestAccountControllerSearch:
    """Test suite for search functionality."""

    def test_search_returns_empty_list(self, mock_services):
        """Test search returns empty list (not implemented yet)."""
        controller = AccountController(account_id=1)
        result = controller.search("test query")

        assert result == []


class TestAccountControllerAsync:
    """Test suite for async methods."""

    @pytest.mark.asyncio
    async def test_start_listening_success(self, mock_services):
        """Test start_listening calls sync service and triggers callback."""
        mock_services["sync_service"].wait_for_mail_changes_async = AsyncMock()
        mock_services["sync_service"].wait_for_mail_changes_async.return_value = AsyncMock()
        mock_services[
            "sync_service"
        ].wait_for_mail_changes_async.return_value.__aiter__.return_value = []

        controller = AccountController(account_id=1)
        callback_called = False

        def test_callback(conversations):
            nonlocal callback_called
            callback_called = True

        controller.set_callback_email_changes(test_callback)

        # Mock get_conversations to avoid complex setup
        with patch.object(controller, "get_conversations", return_value=[]):
            await controller.start_listening()

        assert callback_called
