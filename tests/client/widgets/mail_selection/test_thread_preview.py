import unittest
from datetime import datetime

import flet as ft

from remail.client.widgets.mail_selection.thread_preview import ThreadPreview
from remail.controllers.dtos.conversations import ThreadPreviewDTO


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
        self.clicked = {"called": False, "topic": None}

    def _on_click(self, topic):
        self.clicked["called"] = True
        self.clicked["topic"] = topic

    def test_initialization(self):
        preview = ThreadPreview(self.topic, self._on_click)
        # Prüfen, dass content Row enthält
        self.assertIsInstance(preview.content, ft.Row)
        self.assertEqual(preview.padding, 12)

    def test_texts_display(self):
        preview = ThreadPreview(self.topic, self._on_click)
        column = preview.content.controls[0]
        row_title = column.controls[0].controls[0]
        row_last_message = column.controls[1].controls[0]

        self.assertIn(str(self.topic.unread_count), row_title.value)
        self.assertEqual(row_title.weight, ft.FontWeight.BOLD)
        self.assertEqual(row_last_message.value, self.topic.last_message)

    def test_click_triggers_callback(self):
        preview = ThreadPreview(self.topic, self._on_click)
        # Simuliere Klick
        preview.on_click(None)
        self.assertTrue(self.clicked["called"])
        self.assertEqual(self.clicked["topic"], self.topic)

    def test_no_unread_count(self):
        topic2 = ThreadPreviewDTO(
            thread_id=2,
            title="No Unread",
            total_count=5,
            last_message_datetime=datetime(2025, 12, 3, 12, 0),
            last_message="Nothing unread",
            unread_count=0,
        )
        preview = ThreadPreview(topic2, self._on_click)
        column = preview.content.controls[0]
        row_title = column.controls[0].controls[0]
        self.assertNotIn("(", row_title.value)
        self.assertEqual(row_title.weight, ft.FontWeight.NORMAL)


if __name__ == "__main__":
    unittest.main()
