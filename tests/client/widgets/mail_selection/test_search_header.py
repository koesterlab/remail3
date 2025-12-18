# test_search_header.py
import unittest
from unittest.mock import Mock

from remail.client.state import MainAppState, MainAppStateProperties
from remail.client.widgets.mail_selection.search_header import SearchHeader


class TestSearchHeader(unittest.TestCase):
    def setUp(self):
        self.state = MainAppState()
        self.state.set(MainAppStateProperties.SEARCH_TERM, "initial")
        self.header = SearchHeader(self.state)

    def test_textfield_initial_value(self):
        self.assertEqual(self.header.input.value, "initial")

    def test_textfield_on_change_updates_state(self):
        e = Mock()
        e.control.value = "new term"
        # Trigger on_change
        self.header.input.on_change(e)
        self.assertEqual(self.state.get(MainAppStateProperties.SEARCH_TERM), "new term")

    def test_state_listener_updates_input(self):
        # Ändere den State direkt
        self.state.set(MainAppStateProperties.SEARCH_TERM, "updated")
        self.assertEqual(self.header.input.value, "updated")

    def test_home_button_resets_state(self):
        home_button = self.header.content.controls[0].controls[1]  # Row: [input, home_icon]
        self.state.set(MainAppStateProperties.ACTIVE_THREAD, Mock())
        # Klick simulieren
        home_button.on_click(None)
        self.assertEqual(self.state.get(MainAppStateProperties.SEARCH_TERM), "")
        self.assertIsNone(self.state.get(MainAppStateProperties.ACTIVE_THREAD))


if __name__ == "__main__":
    unittest.main()
