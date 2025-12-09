# test_conversation_selection.py
import unittest
from datetime import datetime
from unittest.mock import Mock

import flet as ft

from remail.client.state import MainAppState
from remail.client.widgets.mail_selection.action import Action
from remail.client.widgets.mail_selection.action_preview import ActionPreview
from remail.client.widgets.mail_selection.contact_preview import ContactPreview
from remail.client.widgets.mail_selection.conversation_selection import ConversationSelection
from remail.client.widgets.mail_selection.group_preview import GroupPreview
from remail.controllers.dtos.conversations import ContactDTO, ConversationDTO, ThreadPreviewDTO
from remail.enums import ContactType


class TestConversationSelection(unittest.TestCase):
    def setUp(self):
        self.state = MainAppState()
        self.callback = Mock()
        self.selection = ConversationSelection(self.callback, self.state)

    def test_container_creation(self):
        self.assertIsInstance(self.selection, ft.Container)
        self.assertIsInstance(self.selection.content, ft.Column)
        # Outer Column hat ScrollMode.AUTO
        self.assertEqual(self.selection.content.scroll, ft.ScrollMode.AUTO)

    def test_set_content_with_action(self):
        action_called = {"called": False}
        action = Action(
            title="Test",
            secondary="Sub",
            on_executed=lambda: action_called.update({"called": True}),
            color=ft.Colors.BLUE,
            icon=ft.Icons.ADD,
        )
        self.selection.set_content([action])
        self.assertEqual(len(self.selection.content.controls), 1)
        item = self.selection.content.controls[0]
        self.assertIsInstance(item, ActionPreview)
        # Callback testen
        item.on_click(None)
        self.callback.assert_called_with(action)

    def test_set_content_with_single_contact(self):
        contact = ContactDTO(
            id=2,
            type=ContactType.PRIVATE,
            first_name="Max",
            last_name="Mustermann",
            email="max@example.com",
            is_known=True,
        )
        conv = ConversationDTO(
            contacts=[contact],
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
        self.selection.set_content([conv])
        self.assertEqual(len(self.selection.content.controls), 1)
        item = self.selection.content.controls[0]
        self.assertIsInstance(item, ContactPreview)
        item.on_click(None)
        self.callback.assert_called_with(conv)

    def test_set_content_with_group(self):
        contact1 = ContactDTO(
            id=2,
            type=ContactType.PRIVATE,
            first_name="Max",
            last_name="Mustermann",
            email="max@example.com",
            is_known=True,
        )
        contact2 = ContactDTO(
            id=3,
            type=ContactType.PRIVATE,
            first_name="John",
            last_name="Doe",
            email="john@example.com",
            is_known=True,
        )
        conv = ConversationDTO(
            contacts=[contact1, contact2],
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
        self.selection.set_content([conv])
        self.assertEqual(len(self.selection.content.controls), 1)
        item = self.selection.content.controls[0]
        self.assertIsInstance(item, GroupPreview)
        item.on_click(None)
        self.callback.assert_called_with(conv)


if __name__ == "__main__":
    unittest.main()
