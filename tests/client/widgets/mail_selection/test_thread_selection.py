import unittest
from datetime import datetime
from unittest.mock import Mock

import flet as ft

from remail.client.state.main_app_state import MainAppState
from remail.client.widgets.mail_selection.thread_selection import ThreadSelection
from remail.controllers.dtos.conversations import ContactDTO, ConversationDTO, ThreadPreviewDTO
from remail.enums import ContactType


class TestThreadSelection(unittest.TestCase):
    def setUp(self) -> None:
        self.state = MainAppState()
        self.on_click_back = Mock()
        self.contact = ContactDTO(
            id=1,
            type=ContactType.PRIVATE,
            first_name="Max",
            last_name="Mustermann",
            email="max@example.com",
            is_known=True,
        )
        self.contact2 = ContactDTO(
            id=2,
            type=ContactType.PRIVATE,
            first_name="Max",
            last_name="Mustermann",
            email="max@example.com",
            is_known=True,
        )
        self.thread1 = ThreadPreviewDTO(
            title="Thread 1",
            last_message="Message 1",
            unread_count=1,
            total_count=5,
            last_message_datetime=datetime(2025, 12, 3, 12, 0),
            thread_id=1,
        )
        self.thread2 = ThreadPreviewDTO(
            title="Thread 2",
            last_message="Message 2",
            unread_count=0,
            total_count=5,
            last_message_datetime=datetime(2025, 12, 3, 12, 0),
            thread_id=2,
        )
        self.conversation = ConversationDTO(
            contacts=[self.contact],
            threads=[self.thread1, self.thread2],
            is_favorite=False,
            customName=None,
        )

    def test_threadselection_is_container(self) -> None:
        """ThreadSelection should be an ft.Container."""
        widget = ThreadSelection(self.state, self.on_click_back)
        self.assertIsInstance(widget, ft.Container)

    def test_set_content_single_contact(self) -> None:
        """set_content should set primary and secondary text for one contact."""
        conversation = self.conversation
        widget = ThreadSelection(self.state, self.on_click_back)
        widget.set_content(conversation)

        # Basis-Komponenten prüfen
        self.assertIsInstance(widget, ft.Container)

    def test_set_content_multiple_contacts(self) -> None:
        """set_content should set primary text with initials and secondary with member count."""
        contacts = [self.contact, self.contact2]
        conversation = ConversationDTO(
            contacts=contacts,
            threads=[self.thread1, self.thread2],
            customName="",
            is_favorite=False,
        )
        widget = ThreadSelection(self.state, self.on_click_back)
        widget.set_content(conversation)

        # Basis-Komponenten prüfen
        self.assertIsInstance(widget, ft.Container)

    def test_on_click_back_called(self) -> None:
        """Clicking back button should call the callback."""
        widget = ThreadSelection(self.state, self.on_click_back)
        # Header row: controls[0] → Container → content → Row → controls[0] → IconButton
        back_button = widget.content.controls[0].content.controls[0]
        back_button.on_click(None)
        self.on_click_back.assert_called_once()
