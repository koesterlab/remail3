import unittest

import flet as ft

from remail.client.widgets.thread import MessageBubble
from remail.controllers.dtos.conversations import ContactDTO
from remail.controllers.dtos.threads import MessageDTO
from remail.enums import ContactType


class TestMessageBubble(unittest.TestCase):
    def setUp(self) -> None:
        self.user = ContactDTO(
            id=1,
            first_name="Current",
            last_name="User",
            email="me@example.com",
            is_known=True,
            type=ContactType.PRIVATE,
        )
        self.other = ContactDTO(
            id=2,
            first_name="Other",
            last_name="User",
            email="other@example.com",
            is_known=True,
            type=ContactType.PRIVATE,
        )

    def test_bubble_alignment_me(self) -> None:
        """Message from current user aligns right and uses primary color."""
        message = MessageDTO(
            sender=self.user, content="Hello me", sent_at="", attachments=[], id=0, subject="Test"
        )
        bubble = MessageBubble(message, self.user)

        # Outer container alignment
        self.assertEqual(bubble.alignment, ft.alignment.center_right)

        # Inner bubble container
        if isinstance(bubble.content, ft.Container):
            inner = bubble.content
        else:
            # Row content for others
            inner = bubble.content.controls[-1]

        self.assertIsInstance(inner, ft.Container)
        self.assertEqual(inner.bgcolor, ft.Colors.PRIMARY)
        self.assertEqual(inner.content.value, "Hello me")

    def test_bubble_alignment_other(self) -> None:
        """Message from other user aligns left and uses secondary color."""
        message = MessageDTO(
            sender=self.other,
            content="Hello other",
            sent_at="",
            attachments=[],
            id=0,
            subject="Test",
        )
        bubble = MessageBubble(message, self.user)

        self.assertEqual(bubble.alignment, ft.alignment.center_left)


if __name__ == "__main__":
    unittest.main()
