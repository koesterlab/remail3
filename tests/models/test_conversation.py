"""Tests for Conversation model."""

from sqlmodel import Session, select

from remail.enums.conversation_type import ConversationType
from remail.enums.protocol import Protocol
from remail.models.contact import Contact
from remail.models.conversation import Conversation
from remail.models.conversation_contact import ConversationContact
from remail.models.user import User
from remail.models.user_conversation import UserConversation


class TestConversationModel:
    """Test suite for Conversation model."""

    def test_create_conversation(self, session: Session):
        """Test creating a conversation."""
        conversation = Conversation(
            custom_name="Test Conversation",
            type=ConversationType.CONVERSATION,
        )
        session.add(conversation)
        session.commit()
        session.refresh(conversation)

        assert conversation.id is not None
        assert conversation.custom_name == "Test Conversation"
        assert conversation.type == ConversationType.CONVERSATION

    def test_create_group_conversation(self, session: Session):
        """Test creating a group conversation."""
        conversation = Conversation(
            custom_name="Group Chat",
            type=ConversationType.GROUP,
        )
        session.add(conversation)
        session.commit()
        session.refresh(conversation)

        assert conversation.type == ConversationType.GROUP
        assert conversation.custom_name == "Group Chat"

    def test_conversation_with_contacts_relationship(self, session: Session):
        """Test conversation relationship with contacts through ConversationContact."""
        # Create conversation
        conversation = Conversation(
            custom_name="Meeting",
            type=ConversationType.CONVERSATION,
        )
        session.add(conversation)
        session.commit()

        # Create contacts
        contact1 = Contact(name="User One", email_address="user1@example.com")
        contact2 = Contact(name="User Two", email_address="user2@example.com")
        session.add(contact1)
        session.add(contact2)
        session.commit()

        # Link contacts to conversation
        conv_contact1 = ConversationContact(conversation_id=conversation.id, contact_id=contact1.id)
        conv_contact2 = ConversationContact(conversation_id=conversation.id, contact_id=contact2.id)
        session.add(conv_contact1)
        session.add(conv_contact2)
        session.commit()

        # Refresh and verify relationships
        session.refresh(conversation)
        assert len(conversation.contacts) == 2
        contact_emails = {contact.email_address for contact in conversation.contacts}
        assert "user1@example.com" in contact_emails
        assert "user2@example.com" in contact_emails

    def test_conversation_with_users_relationship(self, session: Session):
        """Test conversation relationship with users through UserConversation."""
        # Create conversation
        conversation = Conversation(
            custom_name="Project Discussion",
            type=ConversationType.GROUP,
        )
        session.add(conversation)
        session.commit()

        # Create users
        user1 = User(
            name="alice",
            username="alice@example.com",
            host="imap.example.com",
            password="hash1",
            protocol=Protocol.IMAP,
        )
        user2 = User(
            name="bob",
            username="bob@example.com",
            host="imap.example.com",
            password="hash2",
            protocol=Protocol.IMAP,
        )
        session.add(user1)
        session.add(user2)
        session.commit()

        # Link users to conversation
        user_conv1 = UserConversation(
            user_id=user1.id, conversation_id=conversation.id, is_favorite=True
        )
        user_conv2 = UserConversation(
            user_id=user2.id, conversation_id=conversation.id, is_favorite=False
        )
        session.add(user_conv1)
        session.add(user_conv2)
        session.commit()

        # Refresh and verify relationships
        session.refresh(conversation)
        assert len(conversation.users) == 2
        usernames = {user.name for user in conversation.users}
        assert "alice" in usernames
        assert "bob" in usernames

    def test_update_conversation(self, session: Session):
        """Test updating a conversation."""
        conversation = Conversation(
            custom_name="Original Name",
            type=ConversationType.CONVERSATION,
        )
        session.add(conversation)
        session.commit()

        # Update conversation
        conversation.custom_name = "Updated Name"
        session.commit()
        session.refresh(conversation)

        assert conversation.custom_name == "Updated Name"

    def test_delete_conversation(self, session: Session):
        """Test deleting a conversation."""
        conversation = Conversation(
            custom_name="To be deleted",
            type=ConversationType.CONVERSATION,
        )
        session.add(conversation)
        session.commit()
        conversation_id = conversation.id

        # Delete conversation
        session.delete(conversation)
        session.commit()

        # Verify deletion
        statement = select(Conversation).where(Conversation.id == conversation_id)
        result = session.exec(statement).first()
        assert result is None

    def test_query_conversations_by_type(self, session: Session):
        """Test querying conversations by type."""
        # Create conversations with different types
        conv1 = Conversation(
            custom_name="One-on-one",
            type=ConversationType.CONVERSATION,
        )
        conv2 = Conversation(
            custom_name="Team",
            type=ConversationType.GROUP,
        )
        conv3 = Conversation(
            custom_name="Another one-on-one",
            type=ConversationType.CONVERSATION,
        )
        session.add_all([conv1, conv2, conv3])
        session.commit()

        # Query by type
        statement = select(Conversation).where(Conversation.type == ConversationType.CONVERSATION)
        conversations = session.exec(statement).all()

        assert len(conversations) == 2
        for conv in conversations:
            assert conv.type == ConversationType.CONVERSATION

    def test_conversation_type_enum_values(self, session: Session):
        """Test that conversation type enum is properly stored and retrieved."""
        conversation = Conversation(
            custom_name="Enum test",
            type=ConversationType.GROUP,
        )
        session.add(conversation)
        session.commit()
        session.refresh(conversation)

        assert isinstance(conversation.type, ConversationType)
        assert conversation.type == ConversationType.GROUP
        assert conversation.type.value == "group"
