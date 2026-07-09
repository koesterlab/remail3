import unittest
from datetime import datetime

import flet as ft

from remail.client.widgets.thread import MessageBubble
from remail.controllers.dtos.conversations import ContactDTO
from remail.controllers.dtos.threads import MessageContentDTO, MessageDTO, SenderDTO
from remail.enums import ContactType


class TestMessageBubble(unittest.TestCase):
    def setUp(self) -> None:
        self.user_contact = ContactDTO(
            id=1,
            first_name="Current",
            last_name="User",
            email="me@example.com",
            is_known=True,
            type=ContactType.PRIVATE,
        )
        self.user_sender = SenderDTO(
            id=1, first_name="Current", last_name="User", email="me@example.com"
        )
        self.other_sender = SenderDTO(
            id=2, first_name="Other", last_name="User", email="other@example.com"
        )

    def test_bubble_alignment_me(self) -> None:
        """Message from current user aligns right and uses primary color."""
        message = MessageDTO(
            sender=self.user_contact,
            content=MessageContentDTO(body="Hello me", attachments=[]),
            sent_at=datetime(2024, 1, 1),
            id=0,
            subject="Test",
        )
        bubble = MessageBubble(message, self.user_contact)

        # Outer container alignment
        self.assertEqual(bubble.alignment, ft.Alignment.CENTER_RIGHT)

        # Inner bubble container
        if isinstance(bubble.content, ft.Container):
            inner = bubble.content
        else:
            # Row content for others
            inner = bubble.content.controls[-1]

        self.assertIsInstance(inner, ft.Container)
        self.assertEqual(inner.bgcolor, ft.Colors.PRIMARY)
        self.assertEqual(inner.content.controls[0].value, "Hello me")
        self.assertIsNone(bubble.expand)

    def test_bubble_alignment_other(self) -> None:
        """Message from other user aligns left and uses secondary color."""
        message = MessageDTO(
            sender=self.other_sender,
            content=MessageContentDTO(body="Hello other", attachments=[]),
            sent_at=datetime(2024, 1, 1),
            id=0,
            subject="Test",
        )
        bubble = MessageBubble(message, self.user_contact)

        self.assertEqual(bubble.alignment, ft.Alignment.CENTER_LEFT)
        self.assertIsNone(bubble.expand)

    def test_bubble_trims_email_body_outer_space(self) -> None:
        """Message body should not render leading or trailing blank space."""
        message = MessageDTO(
            sender=self.other_sender,
            content=MessageContentDTO(body="\n\nHello other\n\n", attachments=[]),
            sent_at=datetime(2024, 1, 1),
            id=0,
            subject="Test",
        )
        bubble = MessageBubble(message, self.user_contact)
        inner = bubble.content.controls[-1]

        self.assertEqual(inner.content.controls[0].value, "Hello other")
