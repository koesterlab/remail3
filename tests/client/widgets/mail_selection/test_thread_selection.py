# test_thread_selection.py
import unittest
from datetime import datetime
from unittest.mock import Mock

import flet as ft

from remail.client.widgets.mail_selection.thread_selection import ThreadSelection
from remail.controllers.dtos.conversations import ContactDTO, ConversationDTO, ThreadPreviewDTO
from remail.enums import ContactType


class TestThreadSelection(unittest.TestCase):
    def setUp(self):
        self.contact = ContactDTO(
            id=1,
            type=ContactType.PRIVATE,
            first_name="Max",
            last_name="Mustermann",
            email="max@example.com",
            is_known=True,
        )
        self.thread1 = ThreadPreviewDTO(
            title="Thread 1",
            last_message="Message 1",
            unread_count=1,
            total_count=5,
            last_message_datetime=datetime(2025, 12, 3, 12, 0),
            thread_id=1,
        )
        self.thread2 = ThreadPreviewDTO(
            title="Thread 2",
            last_message="Message 2",
            unread_count=0,
            total_count=5,
            last_message_datetime=datetime(2025, 12, 3, 12, 0),
            thread_id=2,
        )
        self.conversation = ConversationDTO(
            contacts=[self.contact],
            threads=[self.thread1, self.thread2],
            is_favorite=False,
            customName=None,
        )
        self.clicked = {"called": False, "thread": None}

    def _on_click(self, thread):
        self.clicked["called"] = True
        self.clicked["thread"] = thread

    def test_initialization(self):
        selection = ThreadSelection(Mock(), self._on_click)
        self.assertIsInstance(selection.controls, list)
        self.assertEqual(len(selection.controls), 2)  # Header + thread_list container

    def test_set_content_single_contact(self):
        selection = ThreadSelection(Mock(), self._on_click)
        selection.set_content(self.conversation)

        # Prüfe Header
        self.assertIsInstance(selection.controls[0], ft.Container)
        header_row = selection.controls[0].content
        self.assertEqual(header_row.controls[1].content.value, "MM")  # Initialien
        self.assertEqual(
            selection.controls[0].content.controls[2].controls[0].value, "Max Mustermann"
        )

        # Prüfe ThreadPreview-Container
        thread_container = selection.controls[1].content.controls[0]
        self.assertEqual(len(thread_container.controls), 2)
        # self.assertEqual(thread_container.controls[0].content.controls[0].controls[0].value, "(1) Thread 1")
        # self.assertEqual(thread_container.controls[1].content.controls[0].controls[0].value, "Thread 2")

    def test_click_callback_on_thread(self):
        selection = ThreadSelection(Mock(), self._on_click)
        selection.set_content(self.conversation)

        # Simuliere Klick auf ersten Thread
        thread_preview = selection.controls[1].content.controls[0].controls[0]
        thread_preview.on_click(None)
        self.assertTrue(self.clicked["called"])
        self.assertEqual(self.clicked["thread"], self.thread1)

    def test_set_content_group(self):
        contact2 = ContactDTO(
            first_name="Anna",
            last_name="Muster",
            email="anna@example.com",
            is_known=True,
            id=2,
            type=ContactType.PRIVATE,
        )
        conversation_group = ConversationDTO(
            contacts=[self.contact, contact2],
            threads=[self.thread1],
            is_favorite=False,
            customName="Test Group",
        )
        selection = ThreadSelection(Mock(), self._on_click)
        selection.set_content(conversation_group)

        self.assertIsInstance(
            selection.controls[0].content.controls[1].content, ft.Icon
        )  # Group Icon
        self.assertEqual(selection.controls[0].content.controls[2].controls[0].value, "Test Group")
        thread_container = selection.controls[1].content.controls[0]
        self.assertEqual(len(thread_container.controls), 1)
        # self.assertEqual(thread_container.controls[0].content.controls[0].controls[0].value, "(1) Thread 1")


if __name__ == "__main__":
    unittest.main()
