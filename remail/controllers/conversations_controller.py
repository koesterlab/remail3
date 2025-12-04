"""Conversations controller for managing conversation operations."""

from __future__ import annotations

from typing import TYPE_CHECKING

from remail.controllers.dtos.conversations import ContactDTO, ConversationDTO
from remail.enums import ContactType
from remail.interfaces.email.services.conversation_service import ConversationService

if TYPE_CHECKING:
    pass


class ConversationsController:
    """Controller for conversation operations."""

    def __init__(self):
        """
        Initialize conversations controller.
        """

        self.service = ConversationService()

    def get_conversations(self, user_id: int) -> list[ConversationDTO]:
        """
        Fetch all conversations for the frontend for a specific user.

        Args:
            user_id: User ID to fetch conversations for

        Returns:
            List of ConversationDTO objects with user-specific favorite status
        """

        conversations_data = self.service.get_all_conversations(user_id)

        return [
            ConversationDTO(
                contacts=[
                    ContactDTO(
                        id=c["id"],
                        first_name=c["first_name"],
                        last_name=c["last_name"],
                        email=c["email"],
                        is_known=c["is_known"],
                        type=ContactType(c["type"]),
                    )
                    for c in conv["contacts"]
                ],
                threads=[],  # TODO: Implement thread fetching
                is_favorite=conv["is_favorite"],
                customName=conv["custom_name"],
            )
            for conv in conversations_data
        ]
