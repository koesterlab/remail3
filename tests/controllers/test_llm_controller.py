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
def controller(mock_llm_service):
    """Create an LLMController instance with mocked service."""
    return LLMController()


class TestInitialization:
    """Tests for controller initialization."""

    def test_controller_initializes_with_system_message(self, controller):
        """Test that controller initializes with a system message."""
        assert len(controller.conversation_history) == 1
        assert controller.conversation_history[0].role == LLMMessageRole.SYSTEM
        assert "Alfred" in controller.conversation_history[0].content
        assert "concise" in controller.conversation_history[0].content

    def test_controller_has_service(self, controller, mock_llm_service):
        """Test that controller has LLM service."""
        assert controller.service == mock_llm_service


class TestChat:
    """Tests for chat method."""

    def test_chat_success(self, controller, mock_llm_service):
        """Test successful chat response."""
        mock_response = MagicMock(spec=LLMCompletionResponse)
        mock_response.completion_text = "Nice to meet you!"
        mock_llm_service.generate_completion_with_history.return_value = mock_response

        result = controller.chat(prompt="Hello, my name is Alice")

        assert isinstance(result, LLMResponseDTO)
        assert result.content == "Nice to meet you!"

    def test_chat_adds_messages_to_history(self, controller, mock_llm_service):
        """Test that chat adds messages to conversation history."""
        mock_response = MagicMock(spec=LLMCompletionResponse)
        mock_response.completion_text = "Response 1"
        mock_llm_service.generate_completion_with_history.return_value = mock_response

        initial_length = len(controller.conversation_history)
        controller.chat(prompt="First message")

        # Should add user message and assistant message
        assert len(controller.conversation_history) == initial_length + 2
        assert controller.conversation_history[-2].role == LLMMessageRole.USER
        assert controller.conversation_history[-2].content == "First message"
        assert controller.conversation_history[-1].role == LLMMessageRole.ASSISTANT
        assert controller.conversation_history[-1].content == "Response 1"

    def test_chat_maintains_conversation_context(self, controller, mock_llm_service):
        """Test that chat maintains conversation context across multiple messages."""
        mock_response_1 = MagicMock(spec=LLMCompletionResponse)
        mock_response_1.completion_text = "First response"
        mock_response_2 = MagicMock(spec=LLMCompletionResponse)
        mock_response_2.completion_text = "Second response"

        mock_llm_service.generate_completion_with_history.side_effect = [
            mock_response_1,
            mock_response_2,
        ]

        controller.chat(prompt="First question")
        controller.chat(prompt="Second question")

        # Should have system message + 2 exchanges (4 messages)
        assert len(controller.conversation_history) == 5
        assert mock_llm_service.generate_completion_with_history.call_count == 2

        # Check that history is passed correctly on second call
        second_call_args = mock_llm_service.generate_completion_with_history.call_args_list[1]
        history_passed = second_call_args.kwargs["conversation_history"]

        # History should include system message + first exchange
        assert len(history_passed) >= 3

    def test_chat_uses_custom_parameters(self, controller, mock_llm_service):
        """Test chat with custom max_tokens and temperature."""
        mock_response = MagicMock(spec=LLMCompletionResponse)
        mock_response.completion_text = "Response"
        mock_llm_service.generate_completion_with_history.return_value = mock_response

        controller.chat(prompt="Test", max_tokens=50, temperature=0.9)

        call_args = mock_llm_service.generate_completion_with_history.call_args
        assert call_args.kwargs["max_tokens"] == 50
        assert call_args.kwargs["temperature"] == 0.9

    def test_chat_uses_default_parameters_from_service(self, controller, mock_llm_service):
        """Test chat uses service defaults when not specified."""
        mock_response = MagicMock(spec=LLMCompletionResponse)
        mock_response.completion_text = "Response"
        mock_llm_service.generate_completion_with_history.return_value = mock_response

        controller.chat(prompt="Test")

        call_args = mock_llm_service.generate_completion_with_history.call_args
        assert call_args.kwargs["max_tokens"] == mock_llm_service.default_max_tokens
        assert call_args.kwargs["temperature"] == mock_llm_service.default_temperature

    def test_chat_raises_on_error(self, controller, mock_llm_service):
        """Test that chat propagates errors."""
        mock_llm_service.generate_completion_with_history.side_effect = RuntimeError(
            "Service unavailable"
        )

        with pytest.raises(RuntimeError, match="Service unavailable"):
            controller.chat(prompt="Test")
