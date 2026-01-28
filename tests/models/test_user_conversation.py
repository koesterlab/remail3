"""Tests for UserConversation model."""

import pytest
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, select

from remail.enums.conversation_type import ConversationType
from remail.enums.protocol import Protocol
from remail.models.conversation import Conversation
from remail.models.user import User
from remail.models.user_conversation import UserConversation


class TestUserConversationModel:
    """Test suite for UserConversation join table."""

    def test_create_user_conversation_link(self, session: Session):
        """Test creating a link between user and conversation."""
        # Create user
        user = User(
            name="testuser",
            username="test@example.com",
            host="imap.example.com",
            password="hash123",
            protocol=Protocol.IMAP,
        )
        session.add(user)

        # Create conversation
        conversation = Conversation(
            custom_name="Test",
            type=ConversationType.CONVERSATION,
        )
        session.add(conversation)
        session.commit()

        # Create link with is_favorite
        user_conv = UserConversation(
            user_id=user.id, conversation_id=conversation.id, is_favorite=True
        )
        session.add(user_conv)
        session.commit()

        # Verify link
        assert user_conv.user_id == user.id
        assert user_conv.conversation_id == conversation.id
        assert user_conv.is_favorite is True

    def test_user_conversation_default_is_favorite(self, session: Session):
        """Test that is_favorite defaults to False."""
        # Create user and conversation
        user = User(
            name="testuser",
            username="test@example.com",
            host="imap.example.com",
            password="hash123",
            protocol=Protocol.IMAP,
        )
        conversation = Conversation(
            custom_name="Test",
            type=ConversationType.CONVERSATION,
        )
        session.add_all([user, conversation])
        session.commit()

        # Create link without specifying is_favorite
        user_conv = UserConversation(user_id=user.id, conversation_id=conversation.id)
        session.add(user_conv)
        session.commit()
        session.refresh(user_conv)

        # Verify default value
        assert user_conv.is_favorite is False

    def test_user_conversation_composite_key(self, session: Session):
        """Test that user_id and conversation_id form a composite primary key."""
        # Create user and conversation
        user = User(
            name="testuser",
            username="test@example.com",
            host="imap.example.com",
            password="hash123",
            protocol=Protocol.IMAP,
        )
        conversation = Conversation(
            custom_name="Test",
            type=ConversationType.CONVERSATION,
        )
        session.add_all([user, conversation])
        session.commit()

        # Create first link
        user_conv1 = UserConversation(
            user_id=user.id, conversation_id=conversation.id, is_favorite=True
        )
        session.add(user_conv1)
        session.commit()

        # Store IDs for duplicate attempt
        user_id = user.id
        conv_id = conversation.id

        # Expunge to avoid identity map conflicts
        session.expunge(user_conv1)

        # Try to create duplicate link (should fail)
        user_conv2 = UserConversation(user_id=user_id, conversation_id=conv_id, is_favorite=False)
        session.add(user_conv2)

        with pytest.raises(IntegrityError):  # Should raise integrity error
            session.flush()

        session.rollback()

    def test_update_is_favorite(self, session: Session):
        """Test updating the is_favorite field."""
        # Create user and conversation
        user = User(
            name="testuser",
            username="test@example.com",
            host="imap.example.com",
            password="hash123",
            protocol=Protocol.IMAP,
        )
        conversation = Conversation(
            custom_name="Test",
            type=ConversationType.CONVERSATION,
        )
        session.add_all([user, conversation])
        session.commit()

        # Create link with is_favorite=False
        user_conv = UserConversation(
            user_id=user.id, conversation_id=conversation.id, is_favorite=False
        )
        session.add(user_conv)
        session.commit()

        # Update to favorite
        user_conv.is_favorite = True
        session.commit()
        session.refresh(user_conv)

        assert user_conv.is_favorite is True

        # Update back to not favorite
        user_conv.is_favorite = False
        session.commit()
        session.refresh(user_conv)

        assert user_conv.is_favorite is False

    def test_multiple_users_per_conversation(self, session: Session):
        """Test that multiple users can have access to the same conversation."""
        # Create conversation
        conversation = Conversation(
            custom_name="Shared Chat",
            type=ConversationType.GROUP,
        )
        session.add(conversation)

        # Create multiple users
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
        user3 = User(
            name="charlie",
            username="charlie@example.com",
            host="imap.example.com",
            password="hash3",
            protocol=Protocol.IMAP,
        )
        session.add_all([user1, user2, user3])
        session.commit()

        # Link all users to conversation with different favorite preferences
        user_conv1 = UserConversation(
            user_id=user1.id, conversation_id=conversation.id, is_favorite=True
        )
        user_conv2 = UserConversation(
            user_id=user2.id, conversation_id=conversation.id, is_favorite=False
        )
        user_conv3 = UserConversation(
            user_id=user3.id, conversation_id=conversation.id, is_favorite=True
        )
        session.add_all([user_conv1, user_conv2, user_conv3])
        session.commit()

        # Query all users for this conversation
        statement = select(UserConversation).where(
            UserConversation.conversation_id == conversation.id
        )
        links = session.exec(statement).all()

        assert len(links) == 3
        user_ids = {link.user_id for link in links}
        assert user1.id in user_ids
        assert user2.id in user_ids
        assert user3.id in user_ids

        # Verify individual favorite preferences
        favorites = {link.user_id: link.is_favorite for link in links}
        assert favorites[user1.id] is True
        assert favorites[user2.id] is False
        assert favorites[user3.id] is True

    def test_multiple_conversations_per_user(self, session: Session):
        """Test that a user can have access to multiple conversations."""
        # Create user
        user = User(
            name="testuser",
            username="test@example.com",
            host="imap.example.com",
            password="hash123",
            protocol=Protocol.IMAP,
        )
        session.add(user)

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

        # Link user to all conversations
        user_conv1 = UserConversation(user_id=user.id, conversation_id=conv1.id, is_favorite=True)
        user_conv2 = UserConversation(user_id=user.id, conversation_id=conv2.id, is_favorite=False)
        user_conv3 = UserConversation(user_id=user.id, conversation_id=conv3.id, is_favorite=True)
        session.add_all([user_conv1, user_conv2, user_conv3])
        session.commit()

        # Query all conversations for this user
        statement = select(UserConversation).where(UserConversation.user_id == user.id)
        links = session.exec(statement).all()

        assert len(links) == 3
        conversation_ids = {link.conversation_id for link in links}
        assert conv1.id in conversation_ids
        assert conv2.id in conversation_ids
        assert conv3.id in conversation_ids

    def test_query_favorite_conversations(self, session: Session):
        """Test querying only favorite conversations for a user."""
        # Create user
        user = User(
            name="testuser",
            username="test@example.com",
            host="imap.example.com",
            password="hash123",
            protocol=Protocol.IMAP,
        )
        session.add(user)

        # Create conversations
        conv1 = Conversation(
            custom_name="Favorite 1",
            type=ConversationType.CONVERSATION,
        )
        conv2 = Conversation(
            custom_name="Not Favorite",
            type=ConversationType.CONVERSATION,
        )
        conv3 = Conversation(
            custom_name="Favorite 2",
            type=ConversationType.GROUP,
        )
        session.add_all([conv1, conv2, conv3])
        session.commit()

        # Link conversations with different favorite settings
        user_conv1 = UserConversation(user_id=user.id, conversation_id=conv1.id, is_favorite=True)
        user_conv2 = UserConversation(user_id=user.id, conversation_id=conv2.id, is_favorite=False)
        user_conv3 = UserConversation(user_id=user.id, conversation_id=conv3.id, is_favorite=True)
        session.add_all([user_conv1, user_conv2, user_conv3])
        session.commit()

        # Query only favorites
        statement = select(UserConversation).where(
            UserConversation.user_id == user.id, UserConversation.is_favorite
        )
        favorite_links = session.exec(statement).all()

        assert len(favorite_links) == 2
        favorite_conv_ids = {link.conversation_id for link in favorite_links}
        assert conv1.id in favorite_conv_ids
        assert conv3.id in favorite_conv_ids
        assert conv2.id not in favorite_conv_ids

    def test_delete_user_conversation_link(self, session: Session):
        """Test deleting a user-conversation link."""
        # Create user and conversation
        user = User(
            name="testuser",
            username="test@example.com",
            host="imap.example.com",
            password="hash123",
            protocol=Protocol.IMAP,
        )
        conversation = Conversation(
            custom_name="Test",
            type=ConversationType.CONVERSATION,
        )
        session.add_all([user, conversation])
        session.commit()

        # Create link
        user_conv = UserConversation(
            user_id=user.id, conversation_id=conversation.id, is_favorite=True
        )
        session.add(user_conv)
        session.commit()

        # Delete link
        session.delete(user_conv)
        session.commit()

        # Verify deletion
        statement = select(UserConversation).where(
            UserConversation.user_id == user.id,
            UserConversation.conversation_id == conversation.id,
        )
        result = session.exec(statement).first()
        assert result is None
