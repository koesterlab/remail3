"""Service for fetching and managing conversations."""

from __future__ import annotations

from sqlmodel import Session, col, select

from remail.database import engine
from remail.enums import ConversationType
from remail.models import Contact, Conversation, ConversationContact, User, UserConversation


class ConversationService:
    """Service for managing conversations."""

    def __init__(self):
        """
        Initialize conversation service.
        """

        self.engine = engine

    def get_all_conversations(self, user_id: int) -> list[dict]:
        """
        Fetch all conversations with their contacts for a specific user.

        Args:
            user_id: User ID to fetch conversations for

        Returns:
            List of conversation dictionaries with contacts and favorite status
        """

        with Session(self.engine) as session:
            user_conversations = session.exec(
                select(Conversation, UserConversation.is_favorite)
                .join(
                    UserConversation,
                    Conversation.id == UserConversation.conversation_id,  # type: ignore[arg-type]
                )
                .where(UserConversation.user_id == user_id)
            ).all()

            result = []

            for conversation, is_favorite in user_conversations:
                contacts = session.exec(
                    select(Contact)
                    .join(
                        ConversationContact,
                        Contact.id == ConversationContact.contact_id,  # type: ignore[arg-type]
                    )
                    .where(ConversationContact.conversation_id == conversation.id)
                ).all()

                result.append(
                    self._build_conversation_dict(
                        conversation,
                        list(contacts),
                        is_favorite,
                    )
                )

            return result

    def get_conversation_by_id(
        self, conversation_id: int, user_id: int | None = None
    ) -> dict | None:
        """
        Fetch a single conversation with its contacts.

        Args:
            conversation_id: Conversation ID to fetch
            user_id: Optional user ID to include favorite status

        Returns:
            Conversation dictionary with contacts and favorite status, or None if not found
        """

        with Session(self.engine) as session:
            conversation = session.get(Conversation, conversation_id)

            if not conversation or conversation.id is None:
                return None

            contacts = session.exec(
                select(Contact)
                .join(
                    ConversationContact,
                    Contact.id == ConversationContact.contact_id,  # type: ignore[arg-type]
                )
                .where(ConversationContact.conversation_id == conversation.id)
            ).all()

            is_favorite = False

            if user_id is not None:
                user_conversation = session.exec(
                    select(UserConversation)
                    .where(UserConversation.user_id == user_id)
                    .where(UserConversation.conversation_id == conversation.id)
                ).first()

                if user_conversation:
                    is_favorite = user_conversation.is_favorite

            return self._build_conversation_dict(conversation, list(contacts), is_favorite)

    def create_conversation(
        self, user_id: int, contact_ids: list[int], custom_name: str | None = None
    ) -> dict | None:
        """
        Create a new conversation for a user or return an existing one.

        Args:
            user_id: User ID to create the conversation for
            contact_ids: List of contact IDs to include
            custom_name: Optional custom name for the conversation

        Returns:
            Conversation dictionary with contacts and favorite status, or None if invalid input
        """

        if not contact_ids:
            return None

        normalized_ids = {contact_id for contact_id in contact_ids if contact_id is not None}

        if not normalized_ids:
            return None

        with Session(self.engine) as session:
            user = session.get(User, user_id)

            if not user:
                return None

            contacts = session.exec(
                select(Contact).where(col(Contact.id).in_(normalized_ids))
            ).all()

            if len(contacts) != len(normalized_ids):
                return None

            conversation = None
            existing_conversations = session.exec(
                select(Conversation)
                .join(UserConversation)
                .where(UserConversation.user_id == user_id)
            ).all()

            for conv in existing_conversations:
                conv_contact_ids = session.exec(
                    select(ConversationContact.contact_id).where(
                        ConversationContact.conversation_id == conv.id
                    )
                ).all()

                if set(conv_contact_ids) == normalized_ids:
                    conversation = conv
                    break

            if conversation is None:
                conversation_type = (
                    ConversationType.GROUP
                    if len(normalized_ids) > 1
                    else ConversationType.CONVERSATION
                )
                conversation = Conversation(custom_name=custom_name, type=conversation_type)
                session.add(conversation)
                session.flush()

                for contact in contacts:
                    conv_contact = ConversationContact(
                        conversation_id=conversation.id,  # type: ignore[arg-type]
                        contact_id=contact.id,  # type: ignore[arg-type]
                    )
                    session.add(conv_contact)

                user_conv = UserConversation(
                    user_id=user_id,
                    conversation_id=conversation.id,  # type: ignore[arg-type]
                    is_favorite=False,
                )
                session.add(user_conv)

            elif custom_name is not None:
                conversation.custom_name = custom_name
                session.add(conversation)

            session.commit()

            if conversation.id is None:
                return None

            contact_models = session.exec(
                select(Contact)
                .join(
                    ConversationContact,
                    Contact.id == ConversationContact.contact_id,  # type: ignore[arg-type]
                )
                .where(ConversationContact.conversation_id == conversation.id)
            ).all()
            user_conversation = session.exec(
                select(UserConversation)
                .where(UserConversation.user_id == user_id)
                .where(UserConversation.conversation_id == conversation.id)
            ).first()

            is_favorite = user_conversation.is_favorite if user_conversation else False

            return self._build_conversation_dict(conversation, list(contact_models), is_favorite)

    def _build_conversation_dict(
        self, conversation: Conversation, contacts: list[Contact], is_favorite: bool
    ) -> dict:
        """
        Build a conversation dictionary with all related data.

        Args:
            conversation: Conversation model instance
            contacts: List of Contact model instances
            is_favorite: Whether the user marked this conversation as favorite

        Returns:
            Dictionary with conversation data including contacts and favorite status
        """
        contacts_data = [self._build_contact_dict(contact) for contact in contacts]

        return {
            "id": conversation.id,
            "contacts": contacts_data,
            "custom_name": conversation.custom_name,
            "type": conversation.type.value,
            "is_favorite": is_favorite,
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
