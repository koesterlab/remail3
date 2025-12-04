# test_search_header.py
import unittest
from unittest.mock import Mock

from remail.client.views.main.state import MainAppState
from remail.client.widgets.mail_selection.search_header import SearchHeader
from remail.enums.email_folders import EmailFolders


class TestSearchHeader(unittest.TestCase):
    def setUp(self):
        self.state = MainAppState()
        self.state.set_search_term("initial")
        self.header = SearchHeader(self.state)

    def test_textfield_initial_value(self):
        self.assertEqual(self.header.input.value, "initial")

    def test_textfield_on_change_updates_state(self):
        e = Mock()
        e.control.value = "new term"
        # Trigger on_change
        self.header.input.on_change(e)
        self.assertEqual(self.state.search_term, "new term")

    def test_state_listener_updates_input(self):
        # Ändere den State direkt
        self.state.set_search_term("updated")
        self.assertEqual(self.header.input.value, "updated")

    def test_home_button_resets_state(self):
        home_button = self.header.content.controls[0].controls[1]  # Row: [input, home_icon]
        self.state.set_active_thread(Mock())
        self.state.set_active_folder(EmailFolders.ARCHIVED)
        # Klick simulieren
        home_button.on_click(None)
        self.assertEqual(self.state.search_term, "")
        self.assertIsNone(self.state.active_thread)
        self.assertEqual(self.state.active_folder, EmailFolders.INBOX)

    def test_archiv_link_sets_active_folder(self):
        archiv_link = self.header.content.controls[1].controls[0]
        archiv_link.on_click(None)
        self.assertEqual(self.state.active_folder, EmailFolders.ARCHIVED)

    def test_spam_link_sets_active_folder(self):
        spam_link = self.header.content.controls[1].controls[1]
        spam_link.on_click(None)
        self.assertEqual(self.state.active_folder, EmailFolders.ARCHIVED)


if __name__ == "__main__":
    unittest.main()
