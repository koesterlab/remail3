"""Tests for ConversationContact model."""

import pytest
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, select

from remail.enums.conversation_type import ConversationType
from remail.models.contact import Contact
from remail.models.conversation import Conversation
from remail.models.conversation_contact import ConversationContact


class TestConversationContactModel:
    """Test suite for ConversationContact join table."""

    def test_create_conversation_contact_link(self, session: Session):
        """Test creating a link between conversation and contact."""
        # Create conversation
        conversation = Conversation(
            custom_name="Test",
            type=ConversationType.CONVERSATION,
        )
        session.add(conversation)

        # Create contact
        contact = Contact(name="Test User", email_address="test@example.com")
        session.add(contact)
        session.commit()

        # Create link
        conv_contact = ConversationContact(conversation_id=conversation.id, contact_id=contact.id)
        session.add(conv_contact)
        session.commit()

        # Verify link
        assert conv_contact.conversation_id == conversation.id
        assert conv_contact.contact_id == contact.id

    def test_conversation_contact_composite_key(self, session: Session):
        """Test that conversation_id and contact_id form a composite primary key."""
        # Create conversation and contact
        conversation = Conversation(
            custom_name="Test",
            type=ConversationType.CONVERSATION,
        )
        contact = Contact(name="Test User", email_address="test@example.com")
        session.add_all([conversation, contact])
        session.commit()

        # Create first link
        conv_contact1 = ConversationContact(conversation_id=conversation.id, contact_id=contact.id)
        session.add(conv_contact1)
        session.commit()

        # Store IDs for duplicate attempt
        conv_id = conversation.id
        contact_id = contact.id

        # Expunge to avoid identity map conflicts
        session.expunge(conv_contact1)

        # Try to create duplicate link (should fail)
        conv_contact2 = ConversationContact(conversation_id=conv_id, contact_id=contact_id)
        session.add(conv_contact2)

        with pytest.raises(IntegrityError):  # Should raise integrity error
            session.flush()

        session.rollback()

    def test_multiple_contacts_per_conversation(self, session: Session):
        """Test that a conversation can have multiple contacts."""
        # Create conversation
        conversation = Conversation(
            custom_name="Group Chat",
            type=ConversationType.GROUP,
        )
        session.add(conversation)

        # Create multiple contacts
        contact1 = Contact(name="User One", email_address="user1@example.com")
        contact2 = Contact(name="User Two", email_address="user2@example.com")
        contact3 = Contact(name="User Three", email_address="user3@example.com")
        session.add_all([contact1, contact2, contact3])
        session.commit()

        # Link all contacts to conversation
        conv_contact1 = ConversationContact(conversation_id=conversation.id, contact_id=contact1.id)
        conv_contact2 = ConversationContact(conversation_id=conversation.id, contact_id=contact2.id)
        conv_contact3 = ConversationContact(conversation_id=conversation.id, contact_id=contact3.id)
        session.add_all([conv_contact1, conv_contact2, conv_contact3])
        session.commit()

        # Query all links for this conversation
        statement = select(ConversationContact).where(
            ConversationContact.conversation_id == conversation.id
        )
        links = session.exec(statement).all()

        assert len(links) == 3
        contact_ids = {link.contact_id for link in links}
        assert contact1.id in contact_ids
        assert contact2.id in contact_ids
        assert contact3.id in contact_ids

    def test_multiple_conversations_per_contact(self, session: Session):
        """Test that a contact can be in multiple conversations."""
        # Create contact
        contact = Contact(name="Test User", email_address="user@example.com")
        session.add(contact)

        # Create multiple conversations
        conv1 = Conversation(
            custom_name="Conv 1",
            type=ConversationType.CONVERSATION,
        )
        conv2 = Conversation(
            custom_name="Conv 2",
            type=ConversationType.CONVERSATION,
        )
        conv3 = Conversation(
            custom_name="Conv 3",
            type=ConversationType.GROUP,
        )
        session.add_all([conv1, conv2, conv3])
        session.commit()

        # Link contact to all conversations
        conv_contact1 = ConversationContact(conversation_id=conv1.id, contact_id=contact.id)
        conv_contact2 = ConversationContact(conversation_id=conv2.id, contact_id=contact.id)
        conv_contact3 = ConversationContact(conversation_id=conv3.id, contact_id=contact.id)
        session.add_all([conv_contact1, conv_contact2, conv_contact3])
        session.commit()

        # Query all conversations for this contact
        statement = select(ConversationContact).where(ConversationContact.contact_id == contact.id)
        links = session.exec(statement).all()

        assert len(links) == 3
        conversation_ids = {link.conversation_id for link in links}
        assert conv1.id in conversation_ids
        assert conv2.id in conversation_ids
        assert conv3.id in conversation_ids

    def test_delete_conversation_contact_link(self, session: Session):
        """Test deleting a conversation-contact link."""
        # Create conversation and contact
        conversation = Conversation(
            custom_name="Test",
            type=ConversationType.CONVERSATION,
        )
        contact = Contact(name="Test User", email_address="test@example.com")
        session.add_all([conversation, contact])
        session.commit()

        # Create link
        conv_contact = ConversationContact(conversation_id=conversation.id, contact_id=contact.id)
        session.add(conv_contact)
        session.commit()

        # Delete link
        session.delete(conv_contact)
        session.commit()

        # Verify deletion
        statement = select(ConversationContact).where(
            ConversationContact.conversation_id == conversation.id,
            ConversationContact.contact_id == contact.id,
        )
        result = session.exec(statement).first()
        assert result is None
