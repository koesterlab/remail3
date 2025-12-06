"""Tests for ConversationService."""

import pytest
from sqlmodel import Session

from remail.enums.contact_type import ContactType
from remail.enums.conversation_type import ConversationType
from remail.enums.protocol import Protocol
from remail.interfaces.email.services.conversation_service import ConversationService
from remail.models.contact import Contact
from remail.models.conversation import Conversation
from remail.models.conversation_contact import ConversationContact
from remail.models.user import User
from remail.models.user_conversation import UserConversation


class TestConversationService:
    """Test suite for ConversationService."""

    @pytest.fixture
    def service(self, session: Session):
        """Create a ConversationService instance."""
        conv_service = ConversationService()
        conv_service.session = session
        return conv_service

    @pytest.fixture
    def user_with_conversations(self, session: Session):
        """Create a user with multiple conversations for testing."""
        # Create user
        user = User(
            name="testuser",
            email="test@example.com",
            password="hash123",
            protocol=Protocol.IMAP,
        )
        session.add(user)
        session.commit()

        # Create contacts
        contact1 = Contact(
            name="John Doe",
            email_address="contact1@example.com",
            first_name="John",
            last_name="Doe",
            contact_type=ContactType.PRIVATE,
            is_known=True,
        )
        contact2 = Contact(
            name="Jane Smith",
            email_address="contact2@example.com",
            first_name="Jane",
            last_name="Smith",
            contact_type=ContactType.BUSINESS,
            is_known=False,
        )
        contact3 = Contact(
            name="Bob Johnson",
            email_address="contact3@example.com",
            first_name="Bob",
            last_name="Johnson",
            contact_type=ContactType.PRIVATE,
            is_known=True,
        )
        session.add_all([contact1, contact2, contact3])
        session.commit()

        # Create conversations
        conv1 = Conversation(
            custom_name="First Conversation",
            type=ConversationType.CONVERSATION,
        )
        conv2 = Conversation(
            custom_name="Second Conversation",
            type=ConversationType.GROUP,
        )
        conv3 = Conversation(
            custom_name="Third Conversation",
            type=ConversationType.CONVERSATION,
        )
        session.add_all([conv1, conv2, conv3])
        session.commit()

        # Link user to conversations
        user_conv1 = UserConversation(user_id=user.id, conversation_id=conv1.id, is_favorite=True)
        user_conv2 = UserConversation(user_id=user.id, conversation_id=conv2.id, is_favorite=False)
        user_conv3 = UserConversation(user_id=user.id, conversation_id=conv3.id, is_favorite=True)
        session.add_all([user_conv1, user_conv2, user_conv3])
        session.commit()

        # Link contacts to conversations
        # Conv1 has contact1
        conv_contact1_1 = ConversationContact(conversation_id=conv1.id, contact_id=contact1.id)
        # Conv2 has contact1 and contact2 (group)
        conv_contact2_1 = ConversationContact(conversation_id=conv2.id, contact_id=contact1.id)
        conv_contact2_2 = ConversationContact(conversation_id=conv2.id, contact_id=contact2.id)
        # Conv3 has contact3
        conv_contact3_1 = ConversationContact(conversation_id=conv3.id, contact_id=contact3.id)
        session.add_all([conv_contact1_1, conv_contact2_1, conv_contact2_2, conv_contact3_1])
        session.commit()

        return user

    def test_get_all_conversations_returns_list(
        self, service: ConversationService, user_with_conversations: User, session: Session
    ):
        """Test that get_all_conversations returns a list."""
        result = service.get_all_conversations(user_with_conversations.id)

        assert isinstance(result, list)

    def test_get_all_conversations_returns_correct_count(
        self, service: ConversationService, user_with_conversations: User, session: Session
    ):
        """Test that get_all_conversations returns all user's conversations."""
        result = service.get_all_conversations(user_with_conversations.id)

        assert len(result) == 3

    def test_get_all_conversations_structure(
        self, service: ConversationService, user_with_conversations: User, session: Session
    ):
        """Test that each conversation has the correct structure."""
        result = service.get_all_conversations(user_with_conversations.id)

        for conversation in result:
            assert "custom_name" in conversation
            assert "type" in conversation
            assert "is_favorite" in conversation
            assert "contacts" in conversation
            assert isinstance(conversation["contacts"], list)

    def test_get_all_conversations_contact_structure(
        self, service: ConversationService, user_with_conversations: User, session: Session
    ):
        """Test that each contact in conversations has the correct structure."""
        result = service.get_all_conversations(user_with_conversations.id)

        for conversation in result:
            for contact in conversation["contacts"]:
                assert "id" in contact
                assert "email" in contact
                assert "first_name" in contact
                assert "last_name" in contact
                assert "type" in contact
                assert "is_known" in contact

    def test_get_all_conversations_includes_favorites(
        self, service: ConversationService, user_with_conversations: User, session: Session
    ):
        """Test that is_favorite is correctly set for each conversation."""
        result = service.get_all_conversations(user_with_conversations.id)

        # Find conversations by subject
        conv1 = next(c for c in result if c["custom_name"] == "First Conversation")
        conv2 = next(c for c in result if c["custom_name"] == "Second Conversation")
        conv3 = next(c for c in result if c["custom_name"] == "Third Conversation")

        assert conv1["is_favorite"] is True
        assert conv2["is_favorite"] is False
        assert conv3["is_favorite"] is True

    def test_get_all_conversations_includes_correct_contacts(
        self, service: ConversationService, user_with_conversations: User, session: Session
    ):
        """Test that each conversation has the correct contacts."""
        result = service.get_all_conversations(user_with_conversations.id)

        # Find conversations by subject
        conv1 = next(c for c in result if c["custom_name"] == "First Conversation")
        conv2 = next(c for c in result if c["custom_name"] == "Second Conversation")
        conv3 = next(c for c in result if c["custom_name"] == "Third Conversation")

        # Conv1 should have 1 contact
        assert len(conv1["contacts"]) == 1
        assert conv1["contacts"][0]["email"] == "contact1@example.com"

        # Conv2 should have 2 contacts (group)
        assert len(conv2["contacts"]) == 2
        emails = {c["email"] for c in conv2["contacts"]}
        assert "contact1@example.com" in emails
        assert "contact2@example.com" in emails

        # Conv3 should have 1 contact
        assert len(conv3["contacts"]) == 1
        assert conv3["contacts"][0]["email"] == "contact3@example.com"

    def test_get_all_conversations_contact_types(
        self, service: ConversationService, user_with_conversations: User, session: Session
    ):
        """Test that contact types are correctly included."""
        result = service.get_all_conversations(user_with_conversations.id)

        conv1 = next(c for c in result if c["custom_name"] == "First Conversation")
        assert conv1["contacts"][0]["type"] == "private"
        assert conv1["contacts"][0]["is_known"] is True

        conv2 = next(c for c in result if c["custom_name"] == "Second Conversation")
        contact_types = {c["type"] for c in conv2["contacts"]}
        assert "private" in contact_types
        assert "business" in contact_types

    def test_get_all_conversations_type_values(
        self, service: ConversationService, user_with_conversations: User, session: Session
    ):
        """Test that conversation types are correctly set."""
        result = service.get_all_conversations(user_with_conversations.id)

        conv1 = next(c for c in result if c["custom_name"] == "First Conversation")
        conv2 = next(c for c in result if c["custom_name"] == "Second Conversation")

        assert conv1["type"] == "conversation"
        assert conv2["type"] == "group"

    def test_get_all_conversations_for_nonexistent_user(self, service: ConversationService):
        """Test getting conversations for a user that doesn't exist."""
        result = service.get_all_conversations(99999)

        assert isinstance(result, list)
        assert len(result) == 0

    def test_get_all_conversations_for_user_without_conversations(self, service, session: Session):
        """Test getting conversations for a user with no conversations."""
        # Create user without conversations
        user = User(
            name="lonely",
            email="lonely@example.com",
            password="hash123",
            protocol=Protocol.IMAP,
        )
        session.add(user)
        session.commit()

        result = service.get_all_conversations(user.id)

        assert isinstance(result, list)
        assert len(result) == 0

    def test_get_all_conversations_multiple_users_isolation(self, service, session: Session):
        """Test that conversations are isolated between users."""
        # Create two users
        user1 = User(
            name="user1", email="user1@example.com", password="hash1", protocol=Protocol.IMAP
        )
        user2 = User(
            name="user2", email="user2@example.com", password="hash2", protocol=Protocol.IMAP
        )
        session.add_all([user1, user2])
        session.commit()

        # Create conversation
        conversation = Conversation(
            custom_name="Shared",
            type=ConversationType.CONVERSATION,
        )
        session.add(conversation)
        session.commit()

        # Link only user1 to conversation
        user_conv1 = UserConversation(
            user_id=user1.id, conversation_id=conversation.id, is_favorite=True
        )
        session.add(user_conv1)
        session.commit()

        # User1 should see the conversation
        result1 = service.get_all_conversations(user1.id)
        assert len(result1) == 1

        # User2 should not see the conversation
        result2 = service.get_all_conversations(user2.id)
        assert len(result2) == 0
