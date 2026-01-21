import unittest
from datetime import datetime

import flet as ft

from remail.client.state import MainAppState
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
        self.state = MainAppState()

    def test_threadlist_is_column(self) -> None:
        """ThreadList should be an ft.Column with expanded property."""
        widget = ThreadList(self.state)
        self.assertIsInstance(widget, ft.Container)
        self.assertTrue(widget.expand)


if __name__ == "__main__":
    unittest.main()
