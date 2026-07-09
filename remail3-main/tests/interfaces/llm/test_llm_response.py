"""Tests for LLM response dataclasses."""

from remail.interfaces.llm.enums.llm_message_role import LLMMessageRole
from remail.interfaces.llm.response import (
    LLMCompletionChoice,
    LLMCompletionMessage,
    LLMCompletionResponse,
    LLMCompletionUsage,
)


def test_llm_completion_message_from_dict():
    """Test creating LLMCompletionMessage from dictionary."""
    data = {
        "role": "assistant",
        "content": "Hello, world!",
        "refusal": None,
        "annotations": None,
        "audio": None,
        "function_call": None,
        "tool_calls": [],
        "reasoning_content": None,
    }

    message = LLMCompletionMessage.from_dict(data)

    assert message.role == LLMMessageRole.ASSISTANT
    assert message.content == "Hello, world!"
    assert message.refusal is None
    assert message.tool_calls == []


def test_llm_completion_message_with_invalid_role():
    """Test that invalid roles default to ASSISTANT."""

    data = {"role": "invalid_role", "content": "Test"}
    message = LLMCompletionMessage.from_dict(data)

    assert message.role == LLMMessageRole.ASSISTANT


def test_llm_completion_choice_from_dict():
    """Test creating LLMCompletionChoice from dictionary."""

    data = {
        "index": 0,
        "message": {
            "role": "assistant",
            "content": "Response text",
        },
        "finish_reason": "stop",
        "logprobs": None,
    }

    choice = LLMCompletionChoice.from_dict(data)

    assert choice.index == 0
    assert choice.message.role == LLMMessageRole.ASSISTANT
    assert choice.message.content == "Response text"
    assert choice.finish_reason == "stop"


def test_llm_completion_choice_message_text():
    """Test message_text property with different content types."""

    choice1 = LLMCompletionChoice(
        index=0,
        message=LLMCompletionMessage(role=LLMMessageRole.ASSISTANT, content="Simple text"),
    )

    assert choice1.message_text == "Simple text"

    choice2 = LLMCompletionChoice(
        index=0,
        message=LLMCompletionMessage(role=LLMMessageRole.ASSISTANT, content=["Part 1", "Part 2"]),
    )

    assert choice2.message_text == "Part 1Part 2"

    choice3 = LLMCompletionChoice(
        index=0,
        message=LLMCompletionMessage(role=LLMMessageRole.ASSISTANT, content=None),
    )

    assert choice3.message_text == ""

    choice4 = LLMCompletionChoice(index=0, message=None)

    assert choice4.message_text == ""


def test_llm_completion_usage_from_dict():
    """Test creating LLMCompletionUsage from dictionary."""

    data = {
        "prompt_tokens": 10,
        "completion_tokens": 20,
        "total_tokens": 30,
        "prompt_tokens_details": None,
    }

    usage = LLMCompletionUsage.from_dict(data)

    assert usage.prompt_tokens == 10
    assert usage.completion_tokens == 20
    assert usage.total_tokens == 30


def test_llm_completion_usage_from_none():
    """Test that from_dict returns None for invalid input."""

    assert LLMCompletionUsage.from_dict(None) is None
    assert LLMCompletionUsage.from_dict("invalid") is None


def test_llm_completion_response_from_dict():
    """Test creating LLMCompletionResponse from dictionary."""

    data = {
        "id": "test-id",
        "object": "chat.completion",
        "created": 1234567890,
        "model": "test-model",
        "choices": [
            {
                "index": 0,
                "message": {"role": "assistant", "content": "Response"},
                "finish_reason": "stop",
            }
        ],
        "usage": {
            "prompt_tokens": 5,
            "completion_tokens": 10,
            "total_tokens": 15,
        },
    }

    response = LLMCompletionResponse.from_dict(data)

    assert response.id == "test-id"
    assert response.object == "chat.completion"
    assert response.created == 1234567890
    assert response.model == "test-model"
    assert len(response.choices) == 1
    assert response.usage.total_tokens == 15


def test_llm_completion_response_completion_text():
    """Test completion_text property returns first choice text."""

    data = {
        "id": "test",
        "object": "chat.completion",
        "created": 0,
        "model": "test",
        "choices": [
            {
                "index": 0,
                "message": {"role": "assistant", "content": "First response"},
                "finish_reason": "stop",
            },
            {
                "index": 1,
                "message": {"role": "assistant", "content": "Second response"},
                "finish_reason": "stop",
            },
        ],
    }

    response = LLMCompletionResponse.from_dict(data)

    assert response.completion_text == "First response"


def test_llm_completion_response_empty_choices():
    """Test completion_text returns empty string when no choices."""

    data = {
        "id": "test",
        "object": "chat.completion",
        "created": 0,
        "model": "test",
        "choices": [],
    }

    response = LLMCompletionResponse.from_dict(data)

    assert response.completion_text == ""


def test_llm_completion_response_to_dict():
    """Test to_dict returns raw payload."""

    data = {
        "id": "test",
        "object": "chat.completion",
        "created": 0,
        "model": "test",
        "choices": [],
    }

    response = LLMCompletionResponse.from_dict(data)

    assert response.to_dict() == data
