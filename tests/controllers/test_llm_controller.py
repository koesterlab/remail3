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
        mock.return_value = service_instance
        yield service_instance


@pytest.fixture
def controller(mock_llm_service, mock_chat_service):
    """Create an LLMController instance with mocked services."""
    return LLMController()


class TestInitialization:
    """Tests for controller initialization."""

    def test_controller_has_services(self, controller, mock_llm_service, mock_chat_service):
        """Test that controller initializes with both services."""
        assert controller.service == mock_llm_service
        assert controller.chat_service == mock_chat_service


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

    @pytest.fixture
    def chat_session(self):
        session = MagicMock()
        session.id = 42
        return session

    def test_chat_success_persists_messages(
        self, controller, mock_llm_service, mock_chat_service, chat_session
    ):
        """Test successful chat response and message persistence."""
        mock_response = MagicMock(spec=LLMCompletionResponse)
        mock_response.completion_text = "Nice to meet you!"
        mock_llm_service.generate_completion_with_history.return_value = mock_response

        mock_chat_service.get_or_create_session.return_value = chat_session
        mock_chat_service.build_thread_context.return_value = "Thread context"
        mock_chat_service.get_session_messages.return_value = [
            LLMMessage(role=LLMMessageRole.USER, content="Earlier message")
        ]

        result = controller.chat(prompt="Hello", user_id=1, thread_id=2)

        assert isinstance(result, LLMResponseDTO)
        assert result.content == "Nice to meet you!"

        call_args = mock_llm_service.generate_completion_with_history.call_args
        history_passed = call_args.kwargs["conversation_history"]

        assert history_passed[0].role == LLMMessageRole.SYSTEM
        assert "Thread context" in history_passed[0].content
        assert history_passed[1].content == "Earlier message"

        mock_chat_service.save_message.assert_any_call(
            chat_session.id, LLMMessageRole.USER, "Hello"
        )
        mock_chat_service.save_message.assert_any_call(
            chat_session.id, LLMMessageRole.ASSISTANT, "Nice to meet you!"
        )

    def test_chat_uses_custom_parameters(
        self, controller, mock_llm_service, mock_chat_service, chat_session
    ):
        """Test chat with custom max_tokens and temperature."""
        mock_response = MagicMock(spec=LLMCompletionResponse)
        mock_response.completion_text = "Response"
        mock_llm_service.generate_completion_with_history.return_value = mock_response

        mock_chat_service.get_or_create_session.return_value = chat_session
        mock_chat_service.build_thread_context.return_value = ""
        mock_chat_service.get_session_messages.return_value = []

        controller.chat(prompt="Test", user_id=1, thread_id=2, max_tokens=50, temperature=0.9)

        call_args = mock_llm_service.generate_completion_with_history.call_args
        assert call_args.kwargs["max_tokens"] == 50
        assert call_args.kwargs["temperature"] == 0.9

    def test_chat_uses_default_parameters_from_service(
        self, controller, mock_llm_service, mock_chat_service, chat_session
    ):
        """Test chat uses service defaults when not specified."""
        mock_response = MagicMock(spec=LLMCompletionResponse)
        mock_response.completion_text = "Response"
        mock_llm_service.generate_completion_with_history.return_value = mock_response

        mock_chat_service.get_or_create_session.return_value = chat_session
        mock_chat_service.build_thread_context.return_value = ""
        mock_chat_service.get_session_messages.return_value = []

        controller.chat(prompt="Test", user_id=1, thread_id=2)

        call_args = mock_llm_service.generate_completion_with_history.call_args
        assert call_args.kwargs["max_tokens"] == mock_llm_service.default_max_tokens
        assert call_args.kwargs["temperature"] == mock_llm_service.default_temperature

    def test_chat_raises_on_error(
        self, controller, mock_llm_service, mock_chat_service, chat_session
    ):
        """Test that chat propagates errors."""
        mock_llm_service.generate_completion_with_history.side_effect = RuntimeError(
            "Service unavailable"
        )
        mock_chat_service.get_or_create_session.return_value = chat_session
        mock_chat_service.build_thread_context.return_value = ""
        mock_chat_service.get_session_messages.return_value = []

        with pytest.raises(RuntimeError, match="Service unavailable"):
            controller.chat(prompt="Test", user_id=1, thread_id=2)


class TestSessionMessages:
    """Tests for session message retrieval and reset."""

    @pytest.fixture
    def chat_session(self):
        session = MagicMock()
        session.id = 7
        return session

    def test_get_session_messages(self, controller, mock_chat_service, chat_session):
        """Test that session messages are fetched via ChatService."""
        mock_chat_service.get_or_create_session.return_value = chat_session
        mock_chat_service.get_session_messages.return_value = [
            LLMMessage(role=LLMMessageRole.ASSISTANT, content="Hi")
        ]

        result = controller.get_session_messages(user_id=1, thread_id=2)

        assert result[0].content == "Hi"
        mock_chat_service.get_session_messages.assert_called_once_with(chat_session.id)

    def test_reset_chat_memory(self, controller, mock_chat_service, chat_session):
        """Test that reset clears session messages."""
        mock_chat_service.get_or_create_session.return_value = chat_session

        controller.reset_chat_memory(user_id=1, thread_id=2)

        mock_chat_service.clear_session_messages.assert_called_once_with(chat_session.id)
