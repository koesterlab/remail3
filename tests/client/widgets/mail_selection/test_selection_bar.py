# test_selection_bar.py
import unittest
from datetime import datetime

import flet as ft

from remail.client.views.main.state import MainAppState
from remail.client.widgets.mail_selection import SelectionBar
from remail.client.widgets.mail_selection.action import Action
from remail.client.widgets.mail_selection.action_preview import ActionPreview
from remail.controllers.dtos.conversations import ContactDTO, ConversationDTO, ThreadPreviewDTO
from remail.enums import ContactType


class TestSelectionBar(unittest.TestCase):
    def setUp(self):
        self.state = MainAppState()
        # Test-Daten: 2 Kontakte
        contact = ContactDTO(
            id=1,
            type=ContactType.PRIVATE,
            first_name="Max",
            last_name="Mustermann",
            email="max@example.com",
            is_known=True,
        )
        self.conv1 = ConversationDTO(
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
        self.conv2 = ConversationDTO(
            contacts=[contact],
            is_favorite=True,
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
        self.state.set_displayed([self.conv1, self.conv2])
        self.bar = SelectionBar(self.state)

    def test_initialization(self):
        # SearchHeader und main_content korrekt gesetzt
        self.assertIsInstance(self.bar.content.controls[0], ft.Container)  # SearchHeader
        self.assertIsInstance(self.bar.main_content, ft.AnimatedSwitcher)

    def test_on_search_change_updates_content(self):
        # Simuliere Eingabe eines normalen Suchbegriffs
        self.bar._SelectionBar__on_search_change("asdfsafasdfasdfasdfadsffasdydhz")
        self.assertEqual(
            len(self.bar.conversation_selection.content.controls), 0
        )  # 2 Konversationen
        # Simuliere Eingabe einer E-Mail
        email = "test@example.com"
        self.bar._SelectionBar__on_search_change(email)
        # 2 Action-Items + evtl vorhandene Konversationen
        self.assertTrue(
            any(
                isinstance(c, ActionPreview)
                for c in self.bar.conversation_selection.content.controls
            )
        )

    def test_on_conversation_selected_shows_topic_selection(self):
        self.bar._SelectionBar__on_conversation_or_action_selected(self.conv1)
        self.assertEqual(self.bar.main_content.content, self.bar.topic_selection)

    def test_on_action_selected_executes(self):
        called = {"executed": False}
        action = Action(
            "Title",
            "Secondary",
            lambda: called.update({"executed": True}),
            ft.Colors.PRIMARY,
            ft.Icons.MAIL,
        )
        self.bar._SelectionBar__on_conversation_or_action_selected(action)
        self.assertTrue(called["executed"])

    def test_search_request_returns_test_data(self):
        # Ohne Suchbegriff
        data = self.bar._SelectionBar__search_request()
        self.assertTrue(all(isinstance(c, ConversationDTO) for c in data))
        # Mit Suchbegriff
        data2 = self.bar._SelectionBar__search_request("abc")
        self.assertTrue(all(isinstance(c, ConversationDTO) for c in data2))


if __name__ == "__main__":
    unittest.main()
