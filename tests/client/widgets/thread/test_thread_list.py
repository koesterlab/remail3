import unittest
from datetime import datetime

import flet as ft

from remail.client.widgets.thread import ThreadList
from remail.controllers.dtos.conversations import (
    ContactDTO,
    ConversationDTO,
    ThreadPreviewDTO,
)
from remail.enums import ContactType


class TestThreadList(unittest.TestCase):
    def setUp(self) -> None:
        self.user = ContactDTO(
            id=1,
            first_name="Current",
            last_name="User",
            email="me@example.com",
            is_known=True,
            type=ContactType.PRIVATE,
        )
        self.thread_preview = ThreadPreviewDTO(
            thread_id=1,
            title="Sample Thread",
            last_message="",
            last_message_datetime=datetime.now(),
            total_count=1,
            unread_count=1,
        )
        self.conversation = ConversationDTO(
            contacts=[self.user], threads=[self.thread_preview], is_favorite=False, customName=None
        )

    def test_threadlist_is_column(self) -> None:
        """ThreadList should be an ft.Column with expanded property."""
        widget = ThreadList(self.thread_preview, self.conversation, self.user)
        self.assertIsInstance(widget, ft.Column)
        self.assertTrue(widget.expand)

    def test_input_row_container(self) -> None:
        """The input_row should be an ft.Container."""
        widget = ThreadList(self.thread_preview, self.conversation, self.user)
        self.assertIsInstance(widget.input_row, ft.Container)

    def test_messages_column_container(self) -> None:
        """Messages column should be wrapped in an ft.Container."""
        widget = ThreadList(self.thread_preview, self.conversation, self.user)
        messages_container = widget.controls[2 - 1]  # messages_column
        self.assertIsInstance(messages_container, ft.Container)


if __name__ == "__main__":
    unittest.main()
