"""Service for fetching and managing conversations."""

from __future__ import annotations

from sqlmodel import Session, select

from remail.models import Contact, Conversation, ConversationContact, UserConversation


class ConversationService:
    """Service for managing conversations."""

    def __init__(self):
        """
        Initialize conversation service.
        """

        self.session = Session()

    def get_all_conversations(self, user_id: int) -> list[dict]:
        """
        Fetch all conversations with their contacts for a specific user.

        Args:
            user_id: User ID to fetch conversations for

        Returns:
            List of conversation dictionaries with contacts and favorite status
        """

        # Get all conversations for this user with favorite status
        user_conversations = self.session.exec(
            select(Conversation, UserConversation.is_favorite)
            .join(
                UserConversation,
                Conversation.id == UserConversation.conversation_id,  # type: ignore[arg-type]
            )
            .where(UserConversation.user_id == user_id)
        ).all()

        result = []

        for conversation, is_favorite in user_conversations:
            contacts = self.session.exec(
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
