"""Tests for ThreadController."""

from unittest.mock import MagicMock, Mock, patch

import pytest

from remail.controllers.dtos.conversations import ConversationDTO
from remail.controllers.dtos.threads import (
    ThreadDTO,
)
from remail.controllers.dtos.user_dto import UserDTO
from remail.controllers.thread_controller import ThreadController
from remail.models import Contact, Conversation, Email, Thread, User


@pytest.fixture
def mock_thread_service():
    """Create a mock ThreadService."""
    with patch("remail.controllers.thread_controller.ThreadService") as mock:
        service_instance = MagicMock()
        mock.return_value = service_instance
        yield service_instance


@pytest.fixture
def controller(mock_thread_service):
    """Create a ThreadController instance with mocked service."""
    return ThreadController()


@pytest.fixture
def mock_thread_model():
    """Create a mock Thread model instance."""
    thread = Mock(spec=Thread)
    thread.id = 1
    thread.title = "Project Discussion"
    thread.conversation_id = 10
    thread.messages = []
    thread.conversation = Mock(spec=Conversation)
    return thread


class TestThreadController:
    """Test suite for ThreadController."""

    def test_controller_initializes_with_service(self, controller, mock_thread_service):
        """Test that controller initializes with ThreadService."""
        assert controller.service == mock_thread_service

    def test_get_thread_success(self, controller, mock_thread_service, mock_thread_model):
        """Test successful thread retrieval."""
        mock_thread_service.get_thread_by_id.return_value = mock_thread_model

        with patch("remail.controllers.thread_controller.ThreadDTO") as mock_dto:
            expected_dto = ThreadDTO(id=1, title="Project Discussion", messages=[])
            mock_dto.from_model.return_value = expected_dto

            result = controller.get_thread(thread_id=1)

            assert result == expected_dto
            mock_thread_service.get_thread_by_id.assert_called_once_with(1)
            mock_dto.from_model.assert_called_once_with(mock_thread_model)

    def test_get_thread_not_found(self, controller, mock_thread_service):
        """Test thread not found scenario."""
        mock_thread_service.get_thread_by_id.return_value = None

        result = controller.get_thread(thread_id=999)

        assert result is None
        mock_thread_service.get_thread_by_id.assert_called_once_with(999)

    def test_get_thread_calls_service_with_correct_id(
        self, controller, mock_thread_service, mock_thread_model
    ):
        """Test that get_thread calls service with correct thread_id."""
        mock_thread_service.get_thread_by_id.return_value = mock_thread_model

        with patch("remail.controllers.thread_controller.ThreadDTO") as mock_dto:
            mock_dto.from_model.return_value = ThreadDTO(id=42, title="Test", messages=[])
            controller.get_thread(thread_id=42)

        mock_thread_service.get_thread_by_id.assert_called_once_with(42)

    def test_get_most_urgent_threads(self, controller, mock_thread_service):
        """Test get_most_urgent_threads returns correct data."""
        mock_results = [(Mock(spec=ThreadDTO), Mock(spec=ConversationDTO), Mock(spec=UserDTO))]
        mock_thread_service.get_most_important_threads.return_value = mock_results

        result = controller.get_most_urgent_threads(count=5)

        assert result == mock_results
        mock_thread_service.get_most_important_threads.assert_called_once_with(count=5)

    def test_get_most_urgent_threads_default_count(self, controller, mock_thread_service):
        """Test get_most_urgent_threads with default count."""
        mock_thread_service.get_most_important_threads.return_value = []

        controller.get_most_urgent_threads()

        mock_thread_service.get_most_important_threads.assert_called_once_with(count=5)

    def test_create_thread(self, controller, mock_thread_service, mock_thread_model):
        """Test create_thread creates and returns ThreadDTO."""
        mock_thread_service.create_thread.return_value = mock_thread_model

        with patch("remail.controllers.thread_controller.ThreadDTO") as mock_dto:
            expected_dto = ThreadDTO(id=1, title="New Thread", messages=[])
            mock_dto.from_model.return_value = expected_dto

            result = controller.create_thread(conversation_id=10, name="New Thread")

            assert result == expected_dto
            mock_thread_service.create_thread.assert_called_once_with("New Thread", 10)
            mock_dto.from_model.assert_called_once_with(mock_thread_model)

    def test_send_message(self, controller, mock_thread_service):
        """Test send_message sends email via protocol."""
        # Create mock thread with necessary relationships
        mock_user = Mock(spec=User)
        mock_user.name = "John Doe"
        mock_user.email = "john@example.com"
        mock_user.connection = {"host": "imap.example.com"}

        mock_contact = Mock(spec=Contact)
        mock_contact.first_name = "Jane"
        mock_contact.last_name = "Smith"
        mock_contact.email_address = "jane@example.com"

        mock_conversation = Mock(spec=Conversation)
        mock_conversation.user = mock_user
        mock_conversation.contacts = [mock_contact]

        mock_thread = Mock(spec=Thread)
        mock_thread.id = 1
        mock_thread.title = "Test Thread"
        mock_thread.conversation = mock_conversation
        mock_thread.messages = []

        mock_thread_service.get_thread_by_id.return_value = mock_thread

        with patch("remail.controllers.thread_controller.ImapProtocol") as mock_protocol_cls:
            mock_protocol = MagicMock()
            mock_protocol_cls.return_value = mock_protocol

            controller.send_message(
                thread_id=1, message="Hello, this is a test message", attachment=[]
            )

            mock_thread_service.get_thread_by_id.assert_called_once_with(1)
            mock_protocol_cls.assert_called_once_with(serialized=mock_user.connection)
            mock_protocol.send_email.assert_called_once_with(
                sender=("John Doe", "john@example.com"),
                recipients=[("Jane Smith", "jane@example.com")],
                subject="Test Thread",
                msg="Hello, this is a test message",
            )

    def test_send_message_reply_subject(self, controller, mock_thread_service):
        """Test send_message adds Re: prefix for threads with existing messages."""
        mock_user = Mock(spec=User)
        mock_user.name = "John Doe"
        mock_user.email_address = "john@example.com"
        mock_user.connection = {"host": "imap.example.com"}

        mock_contact = Mock(spec=Contact)
        mock_contact.first_name = "Jane"
        mock_contact.last_name = "Smith"
        mock_contact.email_address = "jane@example.com"

        mock_conversation = Mock(spec=Conversation)
        mock_conversation.user = mock_user
        mock_conversation.contacts = [mock_contact]

        mock_message = Mock(spec=Email)

        mock_thread = Mock(spec=Thread)
        mock_thread.id = 1
        mock_thread.title = "Test Thread"
        mock_thread.conversation = mock_conversation
        mock_thread.messages = [mock_message]  # Has existing message

        mock_thread_service.get_thread_by_id.return_value = mock_thread

        with patch("remail.controllers.thread_controller.ImapProtocol") as mock_protocol_cls:
            mock_protocol = MagicMock()
            mock_protocol_cls.return_value = mock_protocol

            controller.send_message(thread_id=1, message="Reply", attachment=[])

            call_args = mock_protocol.send_email.call_args
            assert call_args.kwargs["subject"] == "Re: Test Thread"
