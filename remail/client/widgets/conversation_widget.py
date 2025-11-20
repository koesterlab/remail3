from __future__ import annotations

from typing import Any

import flet as ft

from .message_bubble import MessageBubble


class ConversationWidget(ft.Column):
    """Central panel: header + context card + message list + input box."""

    def __init__(self, conversation: dict[str, Any]) -> None:
        super().__init__()
        self.conversation: dict[str, Any] = conversation
        self.spacing = 10
        self.expand = True

        # input box
        self.input_field = ft.TextField(
            hint_text="Type a reply...",
            border_radius=20,
            filled=True,
            bgcolor="white",
            dense=True,
            expand=True,  # make sure that one line can be fullfilled
        )

        self._rebuild()

    def set_conversation(self, conversation: dict[str, Any]) -> None:
        self.conversation = conversation
        self._rebuild()
        self.update()

    def _rebuild(self) -> None:
        conv = self.conversation
        contact_name = str(conv.get("contact_name", ""))
        contact_email = str(conv.get("contact_email", ""))
        last_summary = str(conv.get("last_summary", ""))
        tag = conv.get("tag") or ""
        messages = list(conv.get("messages", []))

        # show the top contact information
        header = ft.Row(
            controls=[
                ft.CircleAvatar(
                    content=ft.Text(contact_name[:2]),
                    radius=20,
                ),
                ft.Column(
                    controls=[
                        ft.Text(contact_name, weight="bold"),
                        ft.Text(contact_email, size=12, color="gray"),
                    ],
                    spacing=2,
                ),
            ],
            alignment=ft.MainAxisAlignment.START,
            spacing=10,
        )

        # “Discussing email” card
        discussing_card = ft.Container(
            width=500,
            bgcolor="white",
            padding=15,
            border_radius=12,
            content=ft.Column(
                controls=[
                    ft.Text("Discussing email:", size=12, color="gray"),
                    ft.Text(tag, weight="bold"),
                    ft.Text(last_summary, size=12, color="gray"),
                ],
                spacing=4,
            ),
        )

        # messages list
        messages_column = ft.Column(
            controls=[MessageBubble(m) for m in messages],
            spacing=8,
            expand=True,  #
        )

        # input row
        input_row = ft.Row(
            controls=[
                self.input_field,
                ft.IconButton(
                    icon=ft.icons.SEND,
                    disabled=True,  # it doesn't work now
                    tooltip="Send (coming soon)",
                ),
            ],
            spacing=10,
            alignment=ft.MainAxisAlignment.END,
        )

        self.controls = [
            header,
            ft.Container(height=10),
            discussing_card,
            ft.Container(height=20),
            messages_column,
            ft.Container(height=8),
            input_row,
        ]
