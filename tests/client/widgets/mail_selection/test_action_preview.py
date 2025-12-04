# test_action_preview.py
import unittest
from unittest.mock import Mock

import flet as ft

from remail.client.widgets.mail_selection.action import Action
from remail.client.widgets.mail_selection.action_preview import ActionPreview


class TestActionPreview(unittest.TestCase):
    def setUp(self):
        # Mock Action
        self.callback = Mock()
        self.action = Action(
            title="Test Title",
            secondary="Secondary Text",
            on_executed=Mock(),
            color=ft.Colors.BLUE,
            icon=ft.Icons.ADD,
        )
        self.preview = ActionPreview(self.action, self.callback)

    def test_container_creation(self):
        # ActionPreview ist ein Container
        self.assertIsInstance(self.preview, ft.Container)
        self.assertIsInstance(self.preview.content, ft.Row)

    def test_avatar_and_texts(self):
        row = self.preview.content
        # Erste Spalte: CircleAvatar
        avatar = row.controls[0]
        self.assertIsInstance(avatar, ft.CircleAvatar)
        self.assertEqual(avatar.color, self.action.color)
        self.assertIsInstance(avatar.content, ft.Icon)

        # Zweite Spalte: Column mit Titel + Secondary
        col = row.controls[1]
        self.assertIsInstance(col, ft.Column)
        title_row = col.controls[0]
        secondary_row = col.controls[1]
        self.assertIsInstance(title_row.controls[0], ft.Text)
        self.assertEqual(title_row.controls[0].value, self.action.title)
        self.assertIsInstance(secondary_row.controls[0], ft.Text)
        self.assertEqual(secondary_row.controls[0].value, self.action.secondary)

    def test_callback_invoked_on_click(self):
        # on_click sollte den callback aufrufen
        self.preview.on_click(None)
        self.callback.assert_called_once()


if __name__ == "__main__":
    unittest.main()
