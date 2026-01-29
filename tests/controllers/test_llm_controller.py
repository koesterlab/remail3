"""Tests for LLMController."""

from unittest.mock import MagicMock, patch

import pytest

from remail.controllers.dtos import LLMResponseDTO
from remail.controllers.llm_controller import LLMController
from remail.interfaces.llm.enums.llm_message_role import LLMMessageRole
from remail.interfaces.llm.response import LLMCompletionResponse


@pytest.fixture
def mock_llm_service():
    """Create a mock LLMService."""
    with patch("remail.controllers.llm_controller.LLMService") as mock:
        service_instance = MagicMock()
        service_instance.default_max_tokens = 150
        service_instance.default_temperature = 0.7
        mock.return_value = service_instance
        yield service_instance


@pytest.fixture
def mock_chat_service():
    """Create a mock ChatService."""
    with patch("remail.controllers.llm_controller.ChatService") as mock:
        service_instance = MagicMock()
        mock.return_value = service_instance
        yield service_instance


@pytest.fixture
def controller(mock_llm_service, mock_chat_service):
    """Create an LLMController instance with mocked service."""
    return LLMController()


class TestInitialization:
    """Tests for controller initialization."""

    def test_controller_initializes_with_base_prompt(self, controller):
        """Test that controller initializes with a base system prompt."""
        assert "Alfred" in controller.base_system_prompt
        assert "concise" in controller.base_system_prompt

    def test_controller_has_services(self, controller, mock_llm_service, mock_chat_service):
        """Test that controller has LLM and chat services."""
        assert controller.service == mock_llm_service
        assert controller.chat_service == mock_chat_service


class TestChat:
    """Tests for chat method."""

    def test_chat_success(self, controller, mock_llm_service, mock_chat_service):
        """Test successful chat response."""
        mock_response = MagicMock(spec=LLMCompletionResponse)
        mock_response.completion_text = "Nice to meet you!"
        mock_llm_service.generate_completion_with_history.return_value = mock_response
        mock_session = MagicMock()
        mock_session.id = 123
        mock_chat_service.get_or_create_session.return_value = mock_session
        mock_chat_service.get_session_messages.return_value = []
        mock_chat_service.build_thread_context.return_value = "Thread title: Hello"

        result = controller.chat(prompt="Hello, my name is Alice", user_id=1, thread_id=2)

        assert isinstance(result, LLMResponseDTO)
        assert result.content == "Nice to meet you!"

    def test_chat_persists_messages(self, controller, mock_llm_service, mock_chat_service):
        """Test that chat persists user and assistant messages."""
        mock_response = MagicMock(spec=LLMCompletionResponse)
        mock_response.completion_text = "Response 1"
        mock_llm_service.generate_completion_with_history.return_value = mock_response
        mock_session = MagicMock()
        mock_session.id = 321
        mock_chat_service.get_or_create_session.return_value = mock_session
        mock_chat_service.get_session_messages.return_value = []
        mock_chat_service.build_thread_context.return_value = ""

        controller.chat(prompt="First message", user_id=1, thread_id=2)

        mock_chat_service.save_message.assert_any_call(
            mock_session.id, LLMMessageRole.USER, "First message"
        )
        mock_chat_service.save_message.assert_any_call(
            mock_session.id, LLMMessageRole.ASSISTANT, "Response 1"
        )

    def test_chat_includes_history_and_context(
        self, controller, mock_llm_service, mock_chat_service
    ):
        """Test that chat includes prior messages and thread context."""
        mock_response = MagicMock(spec=LLMCompletionResponse)
        mock_response.completion_text = "Response"
        mock_llm_service.generate_completion_with_history.return_value = mock_response
        mock_session = MagicMock()
        mock_session.id = 111
        mock_chat_service.get_or_create_session.return_value = mock_session
        mock_chat_service.get_session_messages.return_value = [
            MagicMock(role=LLMMessageRole.USER, content="Previous user"),
            MagicMock(role=LLMMessageRole.ASSISTANT, content="Previous assistant"),
        ]
        mock_chat_service.build_thread_context.return_value = "Thread title: Topic"

        controller.chat(prompt="New question", user_id=1, thread_id=2)

        call_args = mock_llm_service.generate_completion_with_history.call_args
        history_passed = call_args.kwargs["conversation_history"]
        assert history_passed[0].role == LLMMessageRole.SYSTEM
        assert "Thread context:" in history_passed[0].content
        assert "Thread title: Topic" in history_passed[0].content
        assert history_passed[1].role == LLMMessageRole.USER
        assert history_passed[1].content == "Previous user"
        assert history_passed[2].role == LLMMessageRole.ASSISTANT
        assert history_passed[2].content == "Previous assistant"

    def test_chat_uses_custom_parameters(self, controller, mock_llm_service, mock_chat_service):
        """Test chat with custom max_tokens and temperature."""
        mock_response = MagicMock(spec=LLMCompletionResponse)
        mock_response.completion_text = "Response"
        mock_llm_service.generate_completion_with_history.return_value = mock_response
        mock_session = MagicMock()
        mock_session.id = 222
        mock_chat_service.get_or_create_session.return_value = mock_session
        mock_chat_service.get_session_messages.return_value = []
        mock_chat_service.build_thread_context.return_value = ""

        controller.chat(prompt="Test", user_id=1, thread_id=2, max_tokens=50, temperature=0.9)

        call_args = mock_llm_service.generate_completion_with_history.call_args
        assert call_args.kwargs["max_tokens"] == 50
        assert call_args.kwargs["temperature"] == 0.9

    def test_chat_uses_default_parameters_from_service(
        self, controller, mock_llm_service, mock_chat_service
    ):
        """Test chat uses service defaults when not specified."""
        mock_response = MagicMock(spec=LLMCompletionResponse)
        mock_response.completion_text = "Response"
        mock_llm_service.generate_completion_with_history.return_value = mock_response
        mock_session = MagicMock()
        mock_session.id = 333
        mock_chat_service.get_or_create_session.return_value = mock_session
        mock_chat_service.get_session_messages.return_value = []
        mock_chat_service.build_thread_context.return_value = ""

        controller.chat(prompt="Test", user_id=1, thread_id=2)

        call_args = mock_llm_service.generate_completion_with_history.call_args
        assert call_args.kwargs["max_tokens"] == mock_llm_service.default_max_tokens
        assert call_args.kwargs["temperature"] == mock_llm_service.default_temperature

    def test_chat_raises_on_error(self, controller, mock_llm_service, mock_chat_service):
        """Test that chat propagates errors."""
        mock_llm_service.generate_completion_with_history.side_effect = RuntimeError(
            "Service unavailable"
        )
        mock_session = MagicMock()
        mock_session.id = 444
        mock_chat_service.get_or_create_session.return_value = mock_session
        mock_chat_service.get_session_messages.return_value = []
        mock_chat_service.build_thread_context.return_value = ""

        with pytest.raises(RuntimeError, match="Service unavailable"):
            controller.chat(prompt="Test", user_id=1, thread_id=2)
