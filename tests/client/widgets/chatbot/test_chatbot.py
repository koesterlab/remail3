"""Tests for chatbot widget."""

from datetime import datetime
from typing import Any
from unittest.mock import MagicMock, patch

import flet as ft
import pytest

from remail.client.state import MainAppState, MainAppStateProperties
from remail.client.widgets.chatbot.chatbot import create_chatbot
from remail.controllers.dtos import LLMResponseDTO
from remail.controllers.dtos.conversations import ThreadPreviewDTO
from remail.controllers.dtos.user_dto import UserDTO
from remail.enums import Protocol, UserAccountCategory


@pytest.fixture
def mock_llm_controller() -> Any:
    """Create a mock LLMController."""
    with patch("remail.client.widgets.chatbot.chatbot.LLMController") as mock:
        controller_instance = MagicMock()
        mock.return_value = controller_instance
        yield controller_instance


@pytest.fixture
def mock_chat_service() -> Any:
    """Create a mock ChatService."""
    with patch("remail.client.widgets.chatbot.chatbot.ChatService") as mock:
        service_instance = MagicMock()
        session = MagicMock()
        session.id = 1
        service_instance.get_or_create_session.return_value = session
        service_instance.get_session_messages.return_value = []
        mock.return_value = service_instance
        yield service_instance


@pytest.fixture(autouse=True)
def mock_flet_update() -> None:
    """Mock Flet control update methods to avoid page requirement."""
    with patch.object(ft.TextField, "update"), patch.object(ft.ListView, "update"):
        yield


def _create_state_with_thread() -> MainAppState:
    state = MainAppState()
    state.set(
        MainAppStateProperties.ACTIVE_USER,
        UserDTO(
            id=1,
            name="Test User",
            email="test@example.com",
            username="test@example.com",
            host="imap.example.com",
            password="secret",
            category=UserAccountCategory.PRIVATE,
            protocol=Protocol.IMAP,
            unread_conversations=0,
        ),
    )
    state.set(
        MainAppStateProperties.ACTIVE_THREAD,
        ThreadPreviewDTO(
            thread_id=1,
            title="Test Thread",
            total_count=1,
            unread_count=0,
            last_message="Hello",
            last_message_datetime=datetime(2025, 1, 1, 12, 0, 0),
        ),
    )
    return state


class TestCreateChatbot:
    """Tests for create_chatbot function."""

    def test_create_chatbot_returns_container(
        self, mock_llm_controller: Any, mock_chat_service: Any
    ) -> None:
        """Test that create_chatbot returns a Flet Column."""
        chatbot = create_chatbot(MainAppState())
        assert isinstance(chatbot, ft.Container)

    def test_chatbot_initializes_controller(
        self, mock_llm_controller: Any, mock_chat_service: Any
    ) -> None:
        """Test that chatbot initializes LLM controller."""
        create_chatbot(MainAppState())
        assert mock_llm_controller is not None


class TestChatbotInteraction:
    """Tests for chatbot user interaction."""

    def test_send_message_with_empty_input(
        self, mock_llm_controller: Any, mock_chat_service: Any
    ) -> None:
        """Test that empty messages are not sent."""
        chatbot = create_chatbot(_create_state_with_thread())
        input_row = chatbot.content.controls[2]
        message_input = input_row.controls[0]

        message_input.value = "   "
        message_input.on_submit(None)

        mock_llm_controller.chat.assert_not_called()

    def test_send_message_success(self, mock_llm_controller: Any, mock_chat_service: Any) -> None:
        """Test successful message sending."""
        mock_response = LLMResponseDTO(content="Hello! How can I help you?")
        mock_llm_controller.chat.return_value = mock_response

        chatbot = create_chatbot(_create_state_with_thread())
        chat_display = chatbot.content.controls[1]
        input_row = chatbot.content.controls[2]
        message_input = input_row.controls[0]

        message_input.value = "Hello"
        message_input.on_submit(None)

        mock_llm_controller.chat.assert_called_once_with(
            prompt="Hello",
            user_id=1,
            thread_id=1,
            max_tokens=100,
            temperature=0.7,
        )
        assert len(chat_display.controls) >= 2

    def test_send_message_displays_user_message(
        self, mock_llm_controller: Any, mock_chat_service: Any
    ) -> None:
        """Test that user message is displayed."""
        mock_response = LLMResponseDTO(content="AI response")
        mock_llm_controller.chat.return_value = mock_response

        chatbot = create_chatbot(_create_state_with_thread())
        chat_display = chatbot.content.controls[1]
        input_row = chatbot.content.controls[2]
        message_input = input_row.controls[0]

        message_input.value = "Test message"
        message_input.on_submit(None)

        user_messages = [
            ctrl
            for ctrl in chat_display.controls
            if isinstance(ctrl, ft.Text) and "You:" in ctrl.value
        ]
        assert len(user_messages) >= 1
        assert "Test message" in user_messages[0].value

    def test_send_message_displays_ai_response(
        self, mock_llm_controller: Any, mock_chat_service: Any
    ) -> None:
        """Test that AI response is displayed."""
        mock_response = LLMResponseDTO(content="This is the AI response")
        mock_llm_controller.chat.return_value = mock_response

        chatbot = create_chatbot(_create_state_with_thread())
        chat_display = chatbot.content.controls[1]
        input_row = chatbot.content.controls[2]
        message_input = input_row.controls[0]

        message_input.value = "Question"
        message_input.on_submit(None)

        ai_messages = [
            ctrl
            for ctrl in chat_display.controls
            if isinstance(ctrl, ft.Text) and "AI:" in ctrl.value
        ]
        assert len(ai_messages) >= 1
        assert "This is the AI response" in ai_messages[0].value

    def test_send_message_clears_input(
        self, mock_llm_controller: Any, mock_chat_service: Any
    ) -> None:
        """Test that input is cleared after sending."""
        mock_response = LLMResponseDTO(content="Response")
        mock_llm_controller.chat.return_value = mock_response

        chatbot = create_chatbot(_create_state_with_thread())
        input_row = chatbot.content.controls[2]
        message_input = input_row.controls[0]
        message_input.value = "Test"

        message_input.on_submit(None)
        assert message_input.value == ""

    def test_send_message_strips_whitespace(
        self, mock_llm_controller: Any, mock_chat_service: Any
    ) -> None:
        """Test that whitespace is stripped from messages."""
        mock_response = LLMResponseDTO(content="Response")
        mock_llm_controller.chat.return_value = mock_response

        chatbot = create_chatbot(_create_state_with_thread())
        input_row = chatbot.content.controls[2]
        message_input = input_row.controls[0]

        message_input.value = "  Hello World  "
        message_input.on_submit(None)

        mock_llm_controller.chat.assert_called_once()
        call_args = mock_llm_controller.chat.call_args
        assert call_args.kwargs["prompt"] == "Hello World"

    def test_multiple_messages(self, mock_llm_controller: Any, mock_chat_service: Any) -> None:
        """Test sending multiple messages in sequence."""
        responses = [
            LLMResponseDTO(content="First response"),
            LLMResponseDTO(content="Second response"),
        ]
        mock_llm_controller.chat.side_effect = responses

        chatbot = create_chatbot(_create_state_with_thread())
        chat_display = chatbot.content.controls[1]
        input_row = chatbot.content.controls[2]
        message_input = input_row.controls[0]

        message_input.value = "First"
        message_input.on_submit(None)

        message_input.value = "Second"
        message_input.on_submit(None)

        assert mock_llm_controller.chat.call_count == 2
        text_controls = [c for c in chat_display.controls if isinstance(c, ft.Text)]
        assert len(text_controls) >= 4


class TestChatbotErrorHandling:
    """Tests for chatbot error handling."""

    def test_send_message_handles_exception(
        self, mock_llm_controller: Any, mock_chat_service: Any
    ) -> None:
        """Test that exceptions are handled gracefully."""
        mock_llm_controller.chat.side_effect = RuntimeError("Connection failed")

        chatbot = create_chatbot(_create_state_with_thread())
        chat_display = chatbot.content.controls[1]
        message_input = chatbot.content.controls[2].controls[0]

        message_input.value = "Test"
        message_input.on_submit(None)

        error_messages = [
            ctrl
            for ctrl in chat_display.controls
            if isinstance(ctrl, ft.Text) and "LLM Server Unavailable" in ctrl.value
        ]
        assert len(error_messages) >= 1

    def test_error_message_contains_user_input(
        self, mock_llm_controller: Any, mock_chat_service: Any
    ) -> None:
        """Test that error message includes the user's input."""
        mock_llm_controller.chat.side_effect = Exception("Error")

        chatbot = create_chatbot(_create_state_with_thread())
        chat_display = chatbot.content.controls[1]
        message_input = chatbot.content.controls[2].controls[0]

        message_input.value = "My question"
        message_input.on_submit(None)

        error_messages = [
            ctrl
            for ctrl in chat_display.controls
            if isinstance(ctrl, ft.Text) and "My question" in ctrl.value
        ]
        assert len(error_messages) >= 1

    def test_error_message_has_red_color(
        self, mock_llm_controller: Any, mock_chat_service: Any
    ) -> None:
        """Test that error messages are displayed in red."""
        mock_llm_controller.chat.side_effect = Exception("Error")

        chatbot = create_chatbot(_create_state_with_thread())
        chat_display = chatbot.content.controls[1]
        message_input = chatbot.content.controls[2].controls[0]

        message_input.value = "Test"
        message_input.on_submit(None)

        error_messages = [
            ctrl
            for ctrl in chat_display.controls
            if isinstance(ctrl, ft.Text) and "Unavailable" in ctrl.value
        ]
        assert len(error_messages) >= 1
        assert error_messages[0].color == "red"


class TestChatbotSubmit:
    """Tests for message submission via Enter key."""

    def test_on_submit_sends_message(
        self, mock_llm_controller: Any, mock_chat_service: Any
    ) -> None:
        """Test that pressing Enter sends the message."""
        mock_response = LLMResponseDTO(content="Response")
        mock_llm_controller.chat.return_value = mock_response

        chatbot = create_chatbot(_create_state_with_thread())
        input_row = chatbot.content.controls[2]
        message_input = input_row.controls[0]
        message_input.value = "Test via Enter"

        message_input.on_submit(None)
        mock_llm_controller.chat.assert_called_once()
        call_args = mock_llm_controller.chat.call_args
        assert call_args.kwargs["prompt"] == "Test via Enter"
