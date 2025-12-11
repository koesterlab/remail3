"""Tests for ThreadController."""

from datetime import datetime
from unittest.mock import MagicMock, patch

import pytest

from remail.controllers.dtos.threads import (
    MessageDTO,
    SenderDTO,
    ThreadDTO,
)
from remail.controllers.dtos.threads.message import MessageContentDTO
from remail.controllers.thread_controller import ThreadController


@pytest.fixture
def mock_thread_service():
    """Create a mock ThreadService."""
    with patch("remail.controllers.thread_controller.ThreadService") as mock:
        service_instance = MagicMock()
        mock.return_value = service_instance
        yield service_instance


@pytest.fixture
def controller(mock_thread_service):
    """Create a ThreadController instance with mocked service."""
    return ThreadController()


class TestThreadController:
    """Test suite for ThreadController."""

    def test_controller_initializes_with_service(self, controller, mock_thread_service):
        """Test that controller initializes with ThreadService."""
        assert controller.service == mock_thread_service

    def test_get_thread_success(self, controller, mock_thread_service):
        """Test successful thread retrieval."""
        # Mock service response
        mock_thread_dto = ThreadDTO(
            id=1,
            title="Project Discussion",
            messages=[
                MessageDTO(
                    id=101,
                    sender=SenderDTO(
                        id=1,
                        first_name="John",
                        last_name="Doe",
                        email="john@example.com",
                    ),
                    subject="Meeting Reminder",
                    content=MessageContentDTO(
                        body="Hello, how are you?",
                        attachments=[],
                    ),
                    sent_at=datetime(2024, 5, 30, 10, 15, 30),
                )
            ],
        )
        mock_thread_service.get_thread_by_id.return_value = mock_thread_dto

        result = controller.get_thread(thread_id=1)

        assert result == mock_thread_dto
        assert result.id == 1
        assert result.title == "Project Discussion"
        assert len(result.messages) == 1
        mock_thread_service.get_thread_by_id.assert_called_once_with(1)

    def test_get_thread_not_found(self, controller, mock_thread_service):
        """Test thread not found scenario."""
        mock_thread_service.get_thread_by_id.return_value = None

        result = controller.get_thread(thread_id=999)

        assert result is None
        mock_thread_service.get_thread_by_id.assert_called_once_with(999)

    def test_get_thread_calls_service_with_correct_id(self, controller, mock_thread_service):
        """Test that get_thread calls service with correct thread_id."""
        mock_thread_dto = ThreadDTO(id=42, title="Test", messages=[])
        mock_thread_service.get_thread_by_id.return_value = mock_thread_dto

        controller.get_thread(thread_id=42)

        mock_thread_service.get_thread_by_id.assert_called_once_with(42)
