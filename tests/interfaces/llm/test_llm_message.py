"""Tests for LLM message DTO."""

from remail.interfaces.llm.dto import LLMMessage
from remail.interfaces.llm.enums.llm_message_role import LLMMessageRole


def test_llm_message_creation():
    """Test creating an LLMMessage."""
    message = LLMMessage(role=LLMMessageRole.USER, content="Hello")

    assert message.role == LLMMessageRole.USER
    assert message.content == "Hello"


def test_llm_message_to_dict():
    """Test converting LLMMessage to dictionary."""
    message = LLMMessage(role=LLMMessageRole.SYSTEM, content="You are helpful")

    result = message.to_dict()

    assert result == {"role": "system", "content": "You are helpful"}


def test_llm_message_all_roles():
    """Test LLMMessage with different roles."""
    roles = [
        LLMMessageRole.SYSTEM,
        LLMMessageRole.USER,
        LLMMessageRole.ASSISTANT,
    ]

    for role in roles:
        message = LLMMessage(role=role, content="Test")
        assert message.role == role
        assert message.to_dict()["role"] == role.value
