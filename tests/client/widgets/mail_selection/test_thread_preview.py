import unittest
from datetime import datetime

import flet as ft

from remail.client.state import MainAppState, MainAppStateProperties
from remail.client.widgets.mail_selection.thread_preview import ThreadPreview
from remail.controllers.dtos.conversations import ConversationDTO, ThreadPreviewDTO


class TestThreadPreview(unittest.TestCase):
    def setUp(self):
        self.topic = ThreadPreviewDTO(
            thread_id=1,
            title="Test Topic",
            last_message="Last message content",
            total_count=5,
            unread_count=3,
            last_message_datetime=datetime(2025, 12, 3, 12, 0),
        )
        self.conversation = ConversationDTO(
            id=1, contacts=[], threads=[self.topic], is_favorite=False, custom_name=None
        )
        self.clicked = {"called": False, "topic": None}
        self.state = MainAppState()

    def _on_click(self, topic):
        self.clicked["called"] = True
        self.clicked["topic"] = topic

    def test_initialization(self):
        self.state.set(MainAppStateProperties.ACTIVE_THREAD, None)
        preview = ThreadPreview(self.state, self.topic, self.conversation)
        # Prüfen, dass content Row enthält
        self.assertIsInstance(preview.content, ft.Column)
        self.assertEqual(preview.padding, ft.padding.all(12))

    def test_texts_display(self):
        self.state.set(MainAppStateProperties.ACTIVE_THREAD, None)
        preview = ThreadPreview(self.state, self.topic, self.conversation)
        column = preview.content
        row_title = column.controls[0]
        row_last_message = column.controls[1].controls[0]

        self.assertIn(str(self.topic.unread_count), row_title.value)
        self.assertEqual(row_title.weight, ft.FontWeight.BOLD)
        self.assertEqual(row_last_message.value, self.topic.last_message)

    def test_click_triggers_callback(self):
        preview = ThreadPreview(self.state, self.topic, self.conversation)
        # Simuliere Klick
        preview.on_click(None)
        self.assertEqual(self.topic, self.state.get(MainAppStateProperties.ACTIVE_THREAD))
