from remail.controllers.dtos.conversations import (
    ContactDTO,
    ConversationDTO,
    ThreadPreviewDTO,
)
from remail.enums import ContactType
from remail.interfaces.email.services import ConversationService, ThreadService


class ConversationsController:
    """Controller for conversation operations."""

    def __init__(self):
        """
        Initialize conversations controller.
        """

        self.service = ConversationService()
        self.thread_service = ThreadService()

    def get_conversations(self, user_id: int) -> list[ConversationDTO]:
        """
        Fetch all conversations for the frontend for a specific user.

        Args:
            user_id: User ID to fetch conversations for

        Returns:
            List of ConversationDTO objects with user-specific favorite status
        """

        conversations_data = self.service.get_all_conversations(user_id)

        result = []

        for conv in conversations_data:
            conversation_id = conv.get("id")
            thread_data = None

            if conversation_id:
                thread_data = self.thread_service.get_thread_for_conversation(conversation_id)

            result.append(
                ConversationDTO(
                    id=conv["id"],
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
                    threads=[
                        ThreadPreviewDTO(
                            thread_id=thread_data["thread_id"],
                            title=thread_data["title"],
                            total_count=thread_data["total_count"],
                            unread_count=thread_data["unread_count"],
                            last_message=thread_data["last_message"],
                            last_message_datetime=thread_data["last_message_datetime"],
                        )
                    ]
                    if thread_data
                    else [],
                    is_favorite=conv["is_favorite"],
                    custom_name=conv["custom_name"],
                )
            )

        return result
