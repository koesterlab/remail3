import unittest
from unittest.mock import Mock

from remail.client.state import MainAppState


# Dummy DTOs
class ConversationDTO:
    def __init__(self, i):
        self.i = i

    def __eq__(self, o):
        return isinstance(o, ConversationDTO) and o.i == self.i

    def __hash__(self):
        return hash(self.i)


class ThreadPreviewDTO:
    def __init__(self, i):
        self.i = i

    def __eq__(self, o):
        return isinstance(o, ThreadPreviewDTO) and o.i == self.i

    def __hash__(self):
        return hash(self.i)


class TestMainAppState(unittest.TestCase):
    def setUp(self):
        self.state = MainAppState()
        self.item1 = ConversationDTO(1)
        self.item2 = ThreadPreviewDTO(2)

    def test_toggle_selection_adds_and_removes(self):
        self.assertEqual(len(self.state._MainAppState__selected), 0)

        self.state.toggle_selection(self.item1)
        self.assertIn(self.item1, self.state._MainAppState__selected)

        self.state.toggle_selection(self.item1)
        self.assertNotIn(self.item1, self.state._MainAppState__selected)

    def test_selection_callback_called_on_toggle(self):
        cb = Mock()
        self.state.listen_selection(self.item1, cb)

        # Erstes Toggle: wird ausgewählt → callback(True)
        self.state.toggle_selection(self.item1)
        cb.assert_called_once_with(True)

        # Zweites Toggle: wird abgewählt → callback(False)
        self.state.toggle_selection(self.item1)
        cb.assert_called_with(False)
        self.assertEqual(cb.call_count, 2)

    def test_multiple_items_independent(self):
        cb1 = Mock()
        cb2 = Mock()

        self.state.listen_selection(self.item1, cb1)
        self.state.listen_selection(self.item2, cb2)

        self.state.toggle_selection(self.item1)
        cb1.assert_called_once_with(True)
        cb2.assert_not_called()

        self.state.toggle_selection(self.item2)
        cb2.assert_called_once_with(True)

    def test_no_callback_when_not_listening(self):
        # Item ohne Listener → kein Fehler, kein Call
        self.state.toggle_selection(self.item1)
        self.state.toggle_selection(self.item1)
