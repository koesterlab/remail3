"""Tests for LLM service."""

import os
from unittest.mock import Mock, patch

import pytest

from remail.interfaces.llm.dto import LLMMessage
from remail.interfaces.llm.enums.llm_message_role import LLMMessageRole
from remail.interfaces.llm.enums.llm_model import LLMModel
from remail.interfaces.llm.llm_service import LLMService
from remail.interfaces.llm.response import LLMCompletionResponse


@pytest.fixture
def mock_env():
    """Mock environment variables for LLM service."""

    with patch.dict(
        os.environ,
        {
            "LLM_API_KEY": "test-api-key-123",
            "LLM_BASE_URL": "https://test.example.com/v1",
        },
    ):
        yield


@pytest.fixture
def mock_openai_response():
    """Create a mock OpenAI response."""

    return {
        "id": "test-completion-id",
        "object": "chat.completion",
        "created": 1234567890,
        "model": "meta-llama-3.1-8b-instruct",
        "choices": [
            {
                "index": 0,
                "message": {
                    "role": "assistant",
                    "content": "This is a test response",
                    "refusal": None,
                    "annotations": None,
                    "audio": None,
                    "function_call": None,
                    "tool_calls": [],
                    "reasoning_content": None,
                },
                "finish_reason": "stop",
                "stop_reason": None,
                "logprobs": None,
            }
        ],
        "usage": {
            "prompt_tokens": 10,
            "completion_tokens": 20,
            "total_tokens": 30,
            "prompt_tokens_details": None,
        },
        "service_tier": None,
        "system_fingerprint": None,
    }


def test_llm_service_init_requires_api_key():
    """Test that LLMService requires LLM_API_KEY environment variable."""

    with patch.dict(os.environ, {}, clear=True):
        with pytest.raises(ValueError, match="LLM_API_KEY environment variable is required"):
            LLMService()


def test_llm_service_init_with_env_vars(mock_env):
    """Test LLMService initialization with environment variables."""

    service = LLMService()

    assert service.api_key == "test-api-key-123"
    assert service.base_url == "https://test.example.com/v1"
    assert service.model == LLMModel.META_LLAMA_3_1_8B_INSTRUCT
    assert service.default_max_tokens == 150
    assert service.default_temperature == 0.7
    assert service.default_top_p == 1.0


def test_llm_service_init_requires_base_url():
    """Test that LLMService requires LLM_BASE_URL environment variable."""

    with patch.dict(os.environ, {"LLM_API_KEY": "test-key"}, clear=True):
        with pytest.raises(ValueError, match="LLM_BASE_URL environment variable is required"):
            LLMService()


def test_generate_completion_with_history_success(mock_env, mock_openai_response):
    """Test successful completion generation with history."""

    service = LLMService()
    mock_response = Mock()
    mock_response.model_dump.return_value = mock_openai_response
    history = [LLMMessage(role=LLMMessageRole.USER, content="Earlier question")]

    with patch.object(service.client.chat.completions, "create", return_value=mock_response):
        result = service.generate_completion_with_history("Tell me a joke", history)

    assert isinstance(result, LLMCompletionResponse)
    assert result.id == "test-completion-id"
    assert result.model == "meta-llama-3.1-8b-instruct"
    assert len(result.choices) == 1
    assert result.choices[0].message.content == "This is a test response"
    assert result.choices[0].message.role == LLMMessageRole.ASSISTANT
    assert result.usage.total_tokens == 30


def test_generate_completion_with_history_custom_parameters(mock_env, mock_openai_response):
    """Test completion generation with custom parameters."""

    service = LLMService()
    mock_response = Mock()
    mock_response.model_dump.return_value = mock_openai_response
    history = [LLMMessage(role=LLMMessageRole.USER, content="Earlier question")]

    with patch.object(
        service.client.chat.completions, "create", return_value=mock_response
    ) as mock_create:
        service.generate_completion_with_history(
            "Test prompt",
            history,
            max_tokens=1024,
            temperature=0.9,
            top_p=0.95,
        )

        call_args = mock_create.call_args

        assert call_args.kwargs["max_tokens"] == 1024
        assert call_args.kwargs["temperature"] == 0.9
        assert call_args.kwargs["top_p"] == 0.95


def test_generate_completion_with_history_creates_correct_messages(mock_env, mock_openai_response):
    """Test that messages are created correctly."""

    service = LLMService()
    mock_response = Mock()
    mock_response.model_dump.return_value = mock_openai_response
    history = [
        LLMMessage(role=LLMMessageRole.USER, content="Previous user"),
        LLMMessage(role=LLMMessageRole.ASSISTANT, content="Previous assistant"),
    ]

    with patch.object(
        service.client.chat.completions, "create", return_value=mock_response
    ) as mock_create:
        service.generate_completion_with_history("Hello", history)

        call_args = mock_create.call_args
        messages = call_args.kwargs["messages"]

        assert len(messages) == 4
        assert messages[0]["role"] == "system"
        assert (
            messages[0]["content"]
            == "You are a helpful assistant. Your name is Alfred. Provide clear, concise, and helpful responses."
        )
        assert messages[1]["role"] == "user"
        assert messages[1]["content"] == "Previous user"
        assert messages[2]["role"] == "assistant"
        assert messages[2]["content"] == "Previous assistant"
        assert messages[3]["role"] == "user"
        assert messages[3]["content"] == "Hello"


def test_generate_completion_with_history_uses_defaults(mock_env, mock_openai_response):
    """Test that default parameters are used when not overridden."""

    service = LLMService()
    mock_response = Mock()
    mock_response.model_dump.return_value = mock_openai_response
    history = [LLMMessage(role=LLMMessageRole.USER, content="Earlier question")]

    with patch.object(
        service.client.chat.completions, "create", return_value=mock_response
    ) as mock_create:
        service.generate_completion_with_history("Test", history)

        call_args = mock_create.call_args

        assert call_args.kwargs["max_tokens"] == 150
        assert call_args.kwargs["temperature"] == 0.7
        assert call_args.kwargs["top_p"] == 1.0


def test_generate_completion_with_history_api_error(mock_env):
    """Test that API errors are raised as RuntimeError."""

    service = LLMService()
    history = [LLMMessage(role=LLMMessageRole.USER, content="Earlier question")]
    with patch.object(
        service.client.chat.completions,
        "create",
        side_effect=Exception("API connection failed"),
    ):
        with pytest.raises(RuntimeError, match="LLM completion failed: API connection failed"):
            service.generate_completion_with_history("Test", history)


def test_completion_response_text_property(mock_env, mock_openai_response):
    """Test that completion_text property works correctly."""

    service = LLMService()
    mock_response = Mock()
    mock_response.model_dump.return_value = mock_openai_response
    history = [LLMMessage(role=LLMMessageRole.USER, content="Earlier question")]

    with patch.object(service.client.chat.completions, "create", return_value=mock_response):
        result = service.generate_completion_with_history("Test", history)

    assert result.completion_text == "This is a test response"
