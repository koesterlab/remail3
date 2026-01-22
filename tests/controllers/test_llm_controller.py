"""Tests for LLMController."""

from unittest.mock import MagicMock, patch

import pytest

from remail.controllers.dtos import LLMResponseDTO
from remail.controllers.llm_controller import LLMController
from remail.interfaces.llm.dto import LLMMessage
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
        session = MagicMock()
        session.id = 123
        service_instance.get_or_create_session.return_value = session
        service_instance.get_session_messages.return_value = []
        service_instance.build_thread_context.return_value = "Thread context"
        mock.return_value = service_instance
        yield service_instance


@pytest.fixture
def controller(mock_llm_service, mock_chat_service):
    """Create an LLMController instance with mocked services."""
    return LLMController()


class TestInitialization:
    """Tests for controller initialization."""

    def test_controller_initializes_with_base_prompt(self, controller, mock_llm_service):
        """Test that controller initializes with a base prompt."""
        assert "Alfred" in controller.base_system_prompt
        assert "concise" in controller.base_system_prompt
        assert controller.service == mock_llm_service


class TestGenerateCompletion:
    """Tests for generate_completion method."""

    def test_generate_completion_success(self, controller, mock_llm_service):
        """Test successful completion generation."""
        mock_response = MagicMock(spec=LLMCompletionResponse)
        mock_response.completion_text = "This is a test response"
        mock_llm_service.generate_completion.return_value = mock_response

        result = controller.generate_completion(
            prompt="Hello",
            max_tokens=100,
            temperature=0.5,
        )

        assert isinstance(result, LLMResponseDTO)
        assert result.content == "This is a test response"
        mock_llm_service.generate_completion.assert_called_once_with(
            prompt="Hello",
            max_tokens=100,
            temperature=0.5,
        )

    def test_generate_completion_uses_default_params(self, controller, mock_llm_service):
        """Test completion generation with default parameters."""
        mock_response = MagicMock(spec=LLMCompletionResponse)
        mock_response.completion_text = "Response"
        mock_llm_service.generate_completion.return_value = mock_response

        controller.generate_completion(prompt="Test")

        mock_llm_service.generate_completion.assert_called_once()
        call_args = mock_llm_service.generate_completion.call_args
        assert call_args.kwargs["prompt"] == "Test"
        assert call_args.kwargs["max_tokens"] is None
        assert call_args.kwargs["temperature"] is None

    def test_generate_completion_raises_on_error(self, controller, mock_llm_service):
        """Test that errors are propagated."""
        mock_llm_service.generate_completion.side_effect = RuntimeError("LLM failed")

        with pytest.raises(RuntimeError, match="LLM failed"):
            controller.generate_completion(prompt="Test")


class TestChat:
    """Tests for chat method."""

    def test_chat_success(self, controller, mock_llm_service):
        """Test successful chat response."""
        mock_response = MagicMock(spec=LLMCompletionResponse)
        mock_response.completion_text = "Nice to meet you!"
        mock_llm_service.generate_completion_with_history.return_value = mock_response

        result = controller.chat(prompt="Hello", thread_id=10, user_id=99)

        assert isinstance(result, LLMResponseDTO)
        assert result.content == "Nice to meet you!"

    def test_chat_includes_thread_context(self, controller, mock_llm_service, mock_chat_service):
        """Test that thread context is injected into the system prompt."""
        mock_response = MagicMock(spec=LLMCompletionResponse)
        mock_response.completion_text = "Response"
        mock_llm_service.generate_completion_with_history.return_value = mock_response

        controller.chat(prompt="Test", thread_id=1, user_id=2)

        call_args = mock_llm_service.generate_completion_with_history.call_args
        assert "Thread context" in call_args.kwargs["system_prompt"]
        assert controller.base_system_prompt in call_args.kwargs["system_prompt"]
        mock_chat_service.build_thread_context.assert_called_once_with(1)

    def test_chat_uses_conversation_history(self, controller, mock_llm_service, mock_chat_service):
        """Test that persisted messages are passed as conversation history."""
        mock_response = MagicMock(spec=LLMCompletionResponse)
        mock_response.completion_text = "Response"
        mock_llm_service.generate_completion_with_history.return_value = mock_response

        history_message = MagicMock(role=LLMMessageRole.USER, content="Previous")
        mock_chat_service.get_session_messages.return_value = [history_message]

        controller.chat(prompt="Test", thread_id=3, user_id=4)

        call_args = mock_llm_service.generate_completion_with_history.call_args
        history = call_args.kwargs["conversation_history"]
        assert len(history) == 1
        assert isinstance(history[0], LLMMessage)
        assert history[0].content == "Previous"
        assert history[0].role == LLMMessageRole.USER

    def test_chat_persists_messages(self, controller, mock_llm_service, mock_chat_service):
        """Test that user and assistant messages are saved."""
        mock_response = MagicMock(spec=LLMCompletionResponse)
        mock_response.completion_text = "Assistant reply"
        mock_llm_service.generate_completion_with_history.return_value = mock_response

        controller.chat(prompt="Hello", thread_id=5, user_id=6)

        assert mock_chat_service.save_message.call_count == 2
        first_call = mock_chat_service.save_message.call_args_list[0]
        second_call = mock_chat_service.save_message.call_args_list[1]
        assert first_call.kwargs["role"] == LLMMessageRole.USER
        assert first_call.kwargs["content"] == "Hello"
        assert second_call.kwargs["role"] == LLMMessageRole.ASSISTANT
        assert second_call.kwargs["content"] == "Assistant reply"

    def test_chat_uses_custom_parameters(self, controller, mock_llm_service):
        """Test chat with custom max_tokens and temperature."""
        mock_response = MagicMock(spec=LLMCompletionResponse)
        mock_response.completion_text = "Response"
        mock_llm_service.generate_completion_with_history.return_value = mock_response

        controller.chat(prompt="Test", thread_id=7, user_id=8, max_tokens=50, temperature=0.9)

        call_args = mock_llm_service.generate_completion_with_history.call_args
        assert call_args.kwargs["max_tokens"] == 50
        assert call_args.kwargs["temperature"] == 0.9

    def test_chat_uses_default_parameters_from_service(self, controller, mock_llm_service):
        """Test chat uses service defaults when not specified."""
        mock_response = MagicMock(spec=LLMCompletionResponse)
        mock_response.completion_text = "Response"
        mock_llm_service.generate_completion_with_history.return_value = mock_response

        controller.chat(prompt="Test", thread_id=9, user_id=10)

        call_args = mock_llm_service.generate_completion_with_history.call_args
        assert call_args.kwargs["max_tokens"] == mock_llm_service.default_max_tokens
        assert call_args.kwargs["temperature"] == mock_llm_service.default_temperature

    def test_chat_raises_on_error(self, controller, mock_llm_service):
        """Test that chat propagates errors."""
        mock_llm_service.generate_completion_with_history.side_effect = RuntimeError(
            "Service unavailable"
        )

        with pytest.raises(RuntimeError, match="Service unavailable"):
            controller.chat(prompt="Test", thread_id=11, user_id=12)


class TestSessionMessages:
    """Tests for get_session_messages method."""

    def test_get_session_messages_returns_llm_messages(self, controller, mock_chat_service):
        """Test that persisted messages are converted to LLMMessage objects."""
        history_message = MagicMock(role=LLMMessageRole.USER, content="Hello")
        mock_chat_service.get_session_messages.return_value = [history_message]

        result = controller.get_session_messages(user_id=1, thread_id=2)

        assert len(result) == 1
        assert isinstance(result[0], LLMMessage)
        assert result[0].role == LLMMessageRole.USER
        assert result[0].content == "Hello"
