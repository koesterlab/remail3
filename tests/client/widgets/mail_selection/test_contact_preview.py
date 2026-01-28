# test_contact_preview.py
import unittest
from datetime import datetime

from remail.client.state import MainAppState
from remail.client.widgets.mail_selection.contact_preview import ContactPreview
from remail.controllers.dtos.conversations import ContactDTO, ConversationDTO, ThreadPreviewDTO
from remail.enums import ContactType


class TestContactPreview(unittest.TestCase):
    def setUp(self):
        # Kontakt DTO
        self.contact_known = ContactDTO(
            id=1,
            type=ContactType.PRIVATE,
            first_name="Max",
            last_name="Mustermann",
            email="max@example.com",
            is_known=True,
        )
        self.contact_unknown = ContactDTO(
            id=2,
            type=ContactType.PRIVATE,
            first_name="John",
            last_name="",
            email="john@example.com",
            is_known=False,
        )

        # Conversation DTOs
        self.conv_known = ConversationDTO(
            contacts=[self.contact_known],
            is_favorite=False,
            threads=[
                ThreadPreviewDTO(
                    title="Thread 1",
                    last_message="Message 1",
                    unread_count=1,
                    total_count=5,
                    last_message_datetime=datetime(2025, 12, 3, 12, 0),
                    thread_id=1,
                )
            ],
            customName=None,
        )
        self.conv_unknown = ConversationDTO(
            contacts=[self.contact_unknown],
            is_favorite=False,
            threads=[
                ThreadPreviewDTO(
                    title="Thread 1",
                    last_message="Message 1",
                    unread_count=1,
                    total_count=5,
                    last_message_datetime=datetime(2025, 12, 3, 12, 0),
                    thread_id=1,
                )
            ],
            customName=None,
        )

    def test_unknown_contact_preview_creation(self):
        ContactPreview(MainAppState(), self.conv_unknown)
