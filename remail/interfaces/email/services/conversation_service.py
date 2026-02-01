"""Service for fetching and managing conversations."""

from __future__ import annotations

from sqlalchemy import func
from sqlmodel import Session, col, select

from remail.database import engine
from remail.enums import ConversationType
from remail.models import Contact, Conversation, ConversationContact, User
from remail.utils.session_management import session


class ConversationService:
    """Service for managing conversations."""

    def __init__(self):
        """
        Initialize conversation service.
        """

        self.engine = engine

    @session
    def get_all_conversations(self, user_id: int, session: Session) -> list[Conversation]:
        """
        Fetch all conversations with their contacts for a specific user.

        Args:
            user_id: User ID to fetch conversations for

        Returns:
            List of conversation dictionaries with contacts and favorite status
        """
        user = session.get(User, user_id)  #
        if not user:
            return []
        return user.conversations

    @session
    def get_conversation_by_id(
        self,
        conversation_id: int,
        session: Session,
        user_id: int | None = None,
    ) -> dict | None:
        """
        Fetch a single conversation with its contacts.

        Args:
            conversation_id: Conversation ID to fetch
            user_id: Optional user ID to include favorite status

        Returns:
            Conversation dictionary with contacts and favorite status, or None if not found
        """

        conversation = session.get(Conversation, conversation_id)
        if not conversation:
            raise ValueError(f"Conversation with id {conversation_id} not found")
        return self._build_conversation_dict(conversation, conversation.contacts)

    @session
    def create_conversation(
        self,
        conversation_type: ConversationType,
        contacts: list[Contact],
        custom_name: str | None,
        user: User,
        session: Session,
    ) -> Conversation:
        """
        Create a new conversation.

        Args:
            conversation_type: Type of the conversation
            contacts: List of Contact model instances to associate with the conversation
            custom_name: Custom name for the conversation
            user: User model instance to associate with the conversation
            session: injected DB session
        Returns:
            Created Conversation object
        """

        new_conversation = Conversation(
            type=conversation_type if conversation_type else ConversationType.GROUP,
            custom_name=custom_name,
            contacts=contacts,
            users=[user],
        )
        session.add(new_conversation)

        return new_conversation

    def _build_conversation_dict(self, conversation: Conversation, contacts: list[Contact]) -> dict:
        """
        Build a conversation dictionary with all related data.

        Args:
            conversation: Conversation model instance
            contacts: List of Contact model instances

        Returns:
            Dictionary with conversation data including contacts and favorite status
        """
        contacts_data = [self._build_contact_dict(contact) for contact in contacts]

        return {
            "id": conversation.id,
            "contacts": contacts_data,
            "custom_name": conversation.custom_name,
            "type": conversation.type.value,
            "is_favorite": conversation.is_favorite,
        }

    @staticmethod
    def _build_contact_dict(contact: Contact) -> dict:
        """
        Build a contact dictionary.

        Args:
            contact: Contact model instance

        Returns:
            Dictionary with contact data
        """
        return {
            "id": contact.id,
            "first_name": contact.first_name or "",
            "last_name": contact.last_name or "",
            "email": contact.email_address,
            "is_known": contact.is_known,
            "type": contact.contact_type.value,
        }

    @session
    def get_conversation_by_members(
        self, members: list[Contact], session: Session
    ) -> Conversation | None:
        ids = [member.id for member in members if member.id is not None]
        if not ids:
            return None
        stmt = (  # get the conversation with the most common members.
            select(
                Conversation,
                func.count(col(ConversationContact.contact_id)).label("hit_count"),
            )
            .join(ConversationContact)
            .where(col(ConversationContact.contact_id).in_(ids))
            .group_by(col(Conversation.id))
            .order_by(func.count(col(ConversationContact.contact_id)).desc())
            .limit(1)
        )

        result = session.exec(stmt).first()
        if not result:
            return None
        # if the number of common members equals the size of member list, it's the same conversation
        (conversation, member_match_count) = result
        if conversation and member_match_count == len(members):
            return conversation
        else:
            return None
