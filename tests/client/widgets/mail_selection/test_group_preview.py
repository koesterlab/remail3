# test_group_preview.py
import unittest
from datetime import datetime

from remail.client.state import MainAppState
from remail.client.widgets.mail_selection.group_preview import GroupPreview
from remail.controllers.dtos.conversations import ContactDTO, ConversationDTO, ThreadPreviewDTO
from remail.enums import ContactType


class TestGroupPreview(unittest.TestCase):
    def setUp(self):
        self.contact1 = ContactDTO(
            id=1,
            type=ContactType.PRIVATE,
            first_name="Max",
            last_name="Mustermann",
            email="max@example.com",
            is_known=True,
        )
        self.contact2 = ContactDTO(
            id=2,
            type=ContactType.PRIVATE,
            first_name="John",
            last_name="Doe",
            email="john@example.com",
            is_known=True,
        )

    def test_group_preview_without_custom_name(self):
        conv = ConversationDTO(
            contacts=[self.contact1, self.contact2],
            is_favorite=False,
            customName=None,
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
        )
        clicked = {"called": False}

        def on_click():
            clicked["called"] = True

        preview = GroupPreview(MainAppState(), conv, on_click)
        row = preview.content
        col = row.controls[1]

        # Primary Text = "M. Mustermann, J. Doe"
        self.assertIn("M. Mustermann", col.controls[0].controls[0].value)
        self.assertIn("J. Doe", col.controls[0].controls[0].value)

        # Secondary Text = "2 Members"
        self.assertEqual(col.controls[1].controls[0].value, "2 Members")

        # Favoriten Toggle
        self.assertFalse(conv.is_favorite)

        # on_click
        preview.on_click(None)
        self.assertTrue(clicked["called"])

    def test_group_preview_with_custom_name(self):
        conv = ConversationDTO(
            contacts=[self.contact1, self.contact2],
            is_favorite=True,
            customName="My Group",
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
        )
        preview = GroupPreview(MainAppState(), conv)
        col = preview.content.controls[1]
        self.assertEqual(col.controls[0].controls[0].value, "My Group")
        self.assertEqual(col.controls[1].controls[0].value, "2 Members")


if __name__ == "__main__":
    unittest.main()
