# test_action.py
import unittest
from unittest.mock import Mock

import flet

from remail.client.widgets.mail_selection.action import Action


class TestAction(unittest.TestCase):
    def test_action_attributes(self):
        callback = Mock()
        action = Action(
            title="Test Title",
            secondary="Secondary Text",
            on_executed=callback,
            color=flet.Colors.BLUE,
            icon=flet.Icons.ADD,
        )

        # Prüfen, ob die Attribute korrekt gesetzt sind
        self.assertEqual(action.title, "Test Title")
        self.assertEqual(action.secondary, "Secondary Text")
        self.assertEqual(action.color, flet.Colors.BLUE)
        self.assertEqual(action.icon, flet.Icons.ADD)
        self.assertEqual(action.on_executed, callback)

    def test_on_executed_callable(self):
        executed = {"called": False}

        def callback():
            executed["called"] = True

        action = Action(
            title="Test",
            secondary="Test2",
            on_executed=callback,
            color=flet.Colors.RED,
            icon=flet.Icons.DELETE,
        )

        # Callback aufrufen
        action.on_executed()
        self.assertTrue(executed["called"])


if __name__ == "__main__":
    unittest.main()
