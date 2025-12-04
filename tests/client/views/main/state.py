import unittest

from remail.client.views.main.state import MainAppState
from remail.controllers.dtos.conversations import ConversationDTO, ThreadPreviewDTO
from remail.enums.email_folders import EmailFolders


class TestMainAppState(unittest.TestCase):
    # ---------------- Selection ----------------
    def test_toggle_selection_add_remove(self):
        state = MainAppState()
        conv = ConversationDTO(subject="Test", contacts=[])
        called = {}

        def listener(selected: bool):
            called["value"] = selected

        state.listen_selection(conv, listener)

        # initially not selected -> add
        state.toggle_selection(conv)
        self.assertTrue(called["value"])

        # remove
        state.toggle_selection(conv)
        self.assertFalse(called["value"])

    # ---------------- Search Term ----------------
    def test_set_search_term_calls_listener(self):
        state = MainAppState()
        called = {}

        def listener(term: str):
            called["term"] = term

        token = state.listen_search_term(listener)
        state.set_search_term("hello")

        self.assertEqual(state.search_term, "hello")
        self.assertEqual(called["term"], "hello")

        # remove listener
        state.remove_search_term_listener(token)
        state.set_search_term("world")
        self.assertEqual(called["term"], "hello")  # listener not called again

    # ---------------- Active Folder ----------------
    def test_active_folder_listener(self):
        state = MainAppState()
        called = {}

        def listener(folder: EmailFolders):
            called["folder"] = folder

        token = state.listen_active_folder(listener)
        state.set_active_folder(EmailFolders.INBOX)

        self.assertEqual(state.active_folder, EmailFolders.INBOX)
        self.assertEqual(called["folder"], EmailFolders.INBOX)

        state.remove_active_folder_listener(token)
        state.set_active_folder(EmailFolders.SENT)
        self.assertEqual(called["folder"], EmailFolders.INBOX)  # unchanged

    # ---------------- Displayed Conversations ----------------
    def test_displayed_conversations_listener(self):
        state = MainAppState()
        conv = ConversationDTO(subject="Test", contacts=[])
        called = {}

        def listener(convs):
            called["convs"] = convs

        token = state.listen_displayed(listener)
        state.set_displayed([conv])

        self.assertEqual(state.displayed, [conv])
        self.assertEqual(called["convs"], [conv])

        state.remove_displayed_listener(token)
        state.set_displayed([])
        self.assertEqual(called["convs"], [conv])  # unchanged

    # ---------------- Active Thread ----------------
    def test_active_thread_listener(self):
        state = MainAppState()
        thread = ThreadPreviewDTO(subject="Thread Test")
        called = {}

        def listener(th):
            called["thread"] = th

        token = state.listen_active_thread(listener)
        state.set_active_thread(thread)

        self.assertEqual(state.active_thread, thread)
        self.assertEqual(called["thread"], thread)

        state.remove_active_thread_listener(token)
        state.set_active_thread(None)
        self.assertEqual(called["thread"], thread)  # listener removed

    # ---------------- WeakMethod cleanup ----------------
    def test_weak_listener_cleanup(self):
        state = MainAppState()

        class Dummy:
            def callback(self, val):
                self.val = val

        obj = Dummy()
        # token = state.listen_search_term(obj.callback)
        state.set_search_term("test")
        self.assertTrue(hasattr(obj, "val"))

        # delete object
        del obj
        state.set_search_term("new")  # should clean up dead weakrefs
        self.assertEqual(len(state._MainAppState__search_term_listeners), 0)


if __name__ == "__main__":
    unittest.main()
