"""Tests for chatbot widget."""

from unittest.mock import MagicMock, patch

import flet as ft
import pytest

from remail.client.widgets.chatbot.chatbot import create_chatbot
from remail.controllers.dto import LLMResponseDTO


@pytest.fixture
def mock_llm_controller():
    """Create a mock LLMController."""

    with patch("remail.client.widgets.chatbot.chatbot.LLMController") as mock:
        controller_instance = MagicMock()
        mock.return_value = controller_instance

        yield controller_instance


@pytest.fixture(autouse=True)
def mock_flet_update():
    """Mock Flet control update methods to avoid page requirement."""

    with patch.object(ft.TextField, "update"), patch.object(ft.ListView, "update"):
        yield


class TestCreateChatbot:
    """Tests for create_chatbot function."""

    def test_create_chatbot_returns_column(self, mock_llm_controller):
        """Test that create_chatbot returns a Flet Column."""

        chatbot = create_chatbot()

        assert isinstance(chatbot, ft.Column)
        assert chatbot.expand is True

    def test_chatbot_has_required_components(self, mock_llm_controller):
        """Test that chatbot contains title, display, and input."""

        chatbot = create_chatbot()

        assert len(chatbot.controls) == 3
        assert isinstance(chatbot.controls[0], ft.Text)
        assert "Alfred" in chatbot.controls[0].value
        assert isinstance(chatbot.controls[1], ft.ListView)
        assert isinstance(chatbot.controls[2], ft.Row)

    def test_chatbot_initializes_controller(self, mock_llm_controller):
        """Test that chatbot initializes LLM controller."""

        create_chatbot()

        assert mock_llm_controller is not None


class TestChatbotInteraction:
    """Tests for chatbot user interaction."""

    def test_send_message_with_empty_input(self, mock_llm_controller):
        """Test that empty messages are not sent."""

        chatbot = create_chatbot()
        input_row = chatbot.controls[2]
        message_input = input_row.controls[0]
        send_button = input_row.controls[1]

        message_input.value = "   "

        send_button.on_click(None)

        mock_llm_controller.chat.assert_not_called()

    def test_send_message_success(self, mock_llm_controller):
        """Test successful message sending."""

        mock_response = LLMResponseDTO(content="Hello! How can I help you?")
        mock_llm_controller.chat.return_value = mock_response

        chatbot = create_chatbot()
        chat_display = chatbot.controls[1]
        input_row = chatbot.controls[2]
        message_input = input_row.controls[0]
        send_button = input_row.controls[1]

        message_input.value = "Hello"
        send_button.on_click(None)

        mock_llm_controller.chat.assert_called_once_with(
            prompt="Hello",
            max_tokens=100,
            temperature=0.7,
        )

        assert len(chat_display.controls) >= 2

    def test_send_message_displays_user_message(self, mock_llm_controller):
        """Test that user message is displayed."""

        mock_response = LLMResponseDTO(content="AI response")
        mock_llm_controller.chat.return_value = mock_response

        chatbot = create_chatbot()
        chat_display = chatbot.controls[1]
        input_row = chatbot.controls[2]
        message_input = input_row.controls[0]
        send_button = input_row.controls[1]

        message_input.value = "Test message"
        send_button.on_click(None)

        user_messages = [
            ctrl
            for ctrl in chat_display.controls
            if isinstance(ctrl, ft.Text) and "You:" in ctrl.value
        ]

        assert len(user_messages) >= 1
        assert "Test message" in user_messages[0].value

    def test_send_message_displays_ai_response(self, mock_llm_controller):
        """Test that AI response is displayed."""

        mock_response = LLMResponseDTO(content="This is the AI response")
        mock_llm_controller.chat.return_value = mock_response

        chatbot = create_chatbot()
        chat_display = chatbot.controls[1]
        input_row = chatbot.controls[2]
        message_input = input_row.controls[0]
        send_button = input_row.controls[1]
        message_input.value = "Question"
        send_button.on_click(None)

        ai_messages = [
            ctrl
            for ctrl in chat_display.controls
            if isinstance(ctrl, ft.Text) and "AI:" in ctrl.value
        ]

        assert len(ai_messages) >= 1
        assert "This is the AI response" in ai_messages[0].value

    def test_send_message_clears_input(self, mock_llm_controller):
        """Test that input is cleared after sending."""

        mock_response = LLMResponseDTO(content="Response")
        mock_llm_controller.chat.return_value = mock_response
        chatbot = create_chatbot()
        input_row = chatbot.controls[2]
        message_input = input_row.controls[0]
        send_button = input_row.controls[1]
        message_input.value = "Test"

        send_button.on_click(None)

        assert message_input.value == ""

    def test_send_message_strips_whitespace(self, mock_llm_controller):
        """Test that whitespace is stripped from messages."""

        mock_response = LLMResponseDTO(content="Response")
        mock_llm_controller.chat.return_value = mock_response

        chatbot = create_chatbot()
        input_row = chatbot.controls[2]
        message_input = input_row.controls[0]
        send_button = input_row.controls[1]
        message_input.value = "  Hello World  "

        send_button.on_click(None)

        mock_llm_controller.chat.assert_called_once()
        call_args = mock_llm_controller.chat.call_args

        assert call_args.kwargs["prompt"] == "Hello World"

    def test_multiple_messages(self, mock_llm_controller):
        """Test sending multiple messages in sequence."""

        responses = [
            LLMResponseDTO(content="First response"),
            LLMResponseDTO(content="Second response"),
        ]

        mock_llm_controller.chat.side_effect = responses

        chatbot = create_chatbot()
        chat_display = chatbot.controls[1]
        input_row = chatbot.controls[2]
        message_input = input_row.controls[0]
        send_button = input_row.controls[1]

        message_input.value = "First"
        send_button.on_click(None)

        message_input.value = "Second"
        send_button.on_click(None)

        assert mock_llm_controller.chat.call_count == 2

        text_controls = [c for c in chat_display.controls if isinstance(c, ft.Text)]
        assert len(text_controls) >= 4


class TestChatbotErrorHandling:
    """Tests for chatbot error handling."""

    def test_send_message_handles_exception(self, mock_llm_controller):
        """Test that exceptions are handled gracefully."""

        mock_llm_controller.chat.side_effect = RuntimeError("Connection failed")

        chatbot = create_chatbot()
        chat_display = chatbot.controls[1]
        input_row = chatbot.controls[2]
        message_input = input_row.controls[0]
        send_button = input_row.controls[1]

        message_input.value = "Test"
        send_button.on_click(None)

        error_messages = [
            ctrl
            for ctrl in chat_display.controls
            if isinstance(ctrl, ft.Text) and "LLM Server Unavailable" in ctrl.value
        ]

        assert len(error_messages) >= 1

    def test_error_message_contains_user_input(self, mock_llm_controller):
        """Test that error message includes the user's input."""

        mock_llm_controller.chat.side_effect = Exception("Error")

        chatbot = create_chatbot()
        chat_display = chatbot.controls[1]
        input_row = chatbot.controls[2]
        message_input = input_row.controls[0]
        send_button = input_row.controls[1]

        message_input.value = "My question"
        send_button.on_click(None)

        error_messages = [
            ctrl
            for ctrl in chat_display.controls
            if isinstance(ctrl, ft.Text) and "My question" in ctrl.value
        ]

        assert len(error_messages) >= 1

    def test_error_message_has_red_color(self, mock_llm_controller):
        """Test that error messages are displayed in red."""

        mock_llm_controller.chat.side_effect = Exception("Error")

        chatbot = create_chatbot()
        chat_display = chatbot.controls[1]
        input_row = chatbot.controls[2]
        message_input = input_row.controls[0]
        send_button = input_row.controls[1]

        message_input.value = "Test"
        send_button.on_click(None)

        error_messages = [
            ctrl
            for ctrl in chat_display.controls
            if isinstance(ctrl, ft.Text) and "Unavailable" in ctrl.value
        ]

        assert len(error_messages) >= 1
        assert error_messages[0].color == "red"


class TestChatbotSubmit:
    """Tests for message submission via Enter key."""

    def test_on_submit_sends_message(self, mock_llm_controller):
        """Test that pressing Enter sends the message."""

        mock_response = LLMResponseDTO(content="Response")
        mock_llm_controller.chat.return_value = mock_response

        chatbot = create_chatbot()
        input_row = chatbot.controls[2]
        message_input = input_row.controls[0]
        message_input.value = "Test via Enter"

        message_input.on_submit(None)
        mock_llm_controller.chat.assert_called_once()

        call_args = mock_llm_controller.chat.call_args

        assert call_args.kwargs["prompt"] == "Test via Enter"
