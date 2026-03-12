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
