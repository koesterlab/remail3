"""Tests for LLMResponseDTO."""

import pytest

from remail.controllers.dtos import LLMResponseDTO


class TestLLMResponseDTO:
    """Tests for LLMResponseDTO dataclass."""

    def test_create_dto_with_content(self):
        """Test creating DTO with content."""

        dto = LLMResponseDTO(content="Test content")

        assert dto.content == "Test content"

    def test_from_completion_text(self):
        """Test creating DTO from completion text."""

        text = "This is the response text"
        dto = LLMResponseDTO.from_completion_text(text)

        assert isinstance(dto, LLMResponseDTO)
        assert dto.content == "This is the response text"

    def test_from_completion_text_strips_whitespace(self):
        """Test that whitespace is stripped from completion text."""

        text = "  Response with whitespace  \n"
        dto = LLMResponseDTO.from_completion_text(text)

        assert dto.content == "Response with whitespace"

    def test_to_dict(self):
        """Test converting DTO to dictionary."""

        dto = LLMResponseDTO(content="Hello world")
        result = dto.to_dict()

        assert isinstance(result, dict)
        assert result == {"content": "Hello world"}

    def test_to_json(self):
        """Test converting DTO to JSON string."""

        dto = LLMResponseDTO(content="Test response")
        json_str = dto.to_json()

        assert isinstance(json_str, str)
        assert '"content"' in json_str
        assert "Test response" in json_str

    def test_dto_equality(self):
        """Test DTO equality comparison."""

        dto1 = LLMResponseDTO(content="Same content")
        dto2 = LLMResponseDTO(content="Same content")
        dto3 = LLMResponseDTO(content="Different content")

        assert dto1 == dto2
        assert dto1 != dto3

    def test_dto_with_empty_content(self):
        """Test DTO with empty content."""

        dto = LLMResponseDTO(content="")

        assert dto.content == ""
        assert dto.to_dict() == {"content": ""}

    def test_from_completion_text_with_multiline(self):
        """Test creating DTO from multiline text."""

        text = """This is a multiline
        response from the LLM
        with multiple lines"""
        dto = LLMResponseDTO.from_completion_text(text)

        assert "multiline" in dto.content
        assert "multiple lines" in dto.content

    def test_dto_is_immutable_with_slots(self):
        """Test that DTO uses slots (for efficiency)."""

        dto = LLMResponseDTO(content="Test")

        with pytest.raises(AttributeError):
            dto.new_attribute = "value"
