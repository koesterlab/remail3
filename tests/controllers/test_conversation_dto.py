"""Tests for conversation DTOs."""

from datetime import datetime

from remail.controllers.dtos.conversations import ContactDTO, ConversationDTO, ThreadPreviewDTO
from remail.enums import ContactType


class TestContactDTO:
    """Test suite for ContactDTO."""

    def test_create_contact_dto(self):
        """Test creating a ContactDTO."""
        contact = ContactDTO(
            id=1,
            email="test@example.com",
            first_name="John",
            last_name="Doe",
            type=ContactType.PRIVATE,
            is_known=True,
        )

        assert contact.id == 1
        assert contact.email == "test@example.com"
        assert contact.first_name == "John"
        assert contact.last_name == "Doe"
        assert contact.type == ContactType.PRIVATE
        assert contact.is_known is True


class TestThreadPreviewDTO:
    """Test suite for ThreadPreviewDTO."""

    def test_create_thread_preview_dto(self):
        """Test creating a ThreadPreviewDTO."""
        now = datetime.now()
        thread = ThreadPreviewDTO(
            thread_id=1,
            title="Test Thread",
            total_count=5,
            unread_count=2,
            last_message="Hello world",
            last_message_datetime=now,
        )

        assert thread.thread_id == 1
        assert thread.title == "Test Thread"
        assert thread.total_count == 5
        assert thread.unread_count == 2
        assert thread.last_message == "Hello world"
        assert thread.last_message_datetime == now


class TestConversationDTO:
    """Test suite for ConversationDTO."""

    def test_create_conversation_dto(self):
        """Test creating a ConversationDTO."""
        contact1 = ContactDTO(
            id=1,
            email="contact1@example.com",
            first_name="John",
            last_name="Doe",
            type=ContactType.PRIVATE,
            is_known=True,
        )
        contact2 = ContactDTO(
            id=2,
            email="contact2@example.com",
            first_name="Jane",
            last_name="Smith",
            type=ContactType.PRIVATE,
            is_known=False,
        )

        conversation = ConversationDTO(
            customName="Meeting",
            contacts=[contact1, contact2],
            threads=[],
            is_favorite=True,
        )

        assert conversation.customName == "Meeting"
        assert len(conversation.contacts) == 2
        assert conversation.is_favorite is True
        assert conversation.threads == []

    def test_conversation_dto_with_threads(self):
        """Test ConversationDTO with threads."""
        contact = ContactDTO(
            id=1,
            email="test@example.com",
            first_name="John",
            last_name="Doe",
            type=ContactType.PRIVATE,
            is_known=True,
        )

        thread = ThreadPreviewDTO(
            thread_id=1,
            title="Thread 1",
            total_count=3,
            unread_count=1,
            last_message="Test message",
            last_message_datetime=datetime.now(),
        )

        conversation = ConversationDTO(
            customName="Test Subject",
            contacts=[contact],
            threads=[thread],
            is_favorite=True,
        )

        assert conversation.customName == "Test Subject"
        assert conversation.is_favorite is True
        assert len(conversation.contacts) == 1
        assert len(conversation.threads) == 1
        assert conversation.threads[0].thread_id == 1

    def test_conversation_dto_empty_contacts(self):
        """Test ConversationDTO with empty contacts list."""
        conversation = ConversationDTO(
            customName="Empty Contacts",
            contacts=[],
            threads=[],
            is_favorite=False,
        )

        assert len(conversation.contacts) == 0
        assert len(conversation.threads) == 0

    def test_conversation_dto_no_custom_name(self):
        """Test ConversationDTO with None as customName."""
        contact = ContactDTO(
            id=1,
            email="test@example.com",
            first_name="John",
            last_name="Doe",
            type=ContactType.PRIVATE,
            is_known=True,
        )

        conversation = ConversationDTO(
            customName=None,
            contacts=[contact],
            threads=[],
            is_favorite=False,
        )

        assert conversation.customName is None
        assert len(conversation.contacts) == 1
