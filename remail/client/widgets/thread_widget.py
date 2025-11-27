# ---------------------------------------------------------------------- #
# Self-test entry: Allows you to run this file directly for preview.
#   (pixi) python -m remail.client.widgets.thread_widget
# ---------------------------------------------------------------------- #
from __future__ import annotations

from typing import Any

import flet as ft

from ..partials.message_bubble import MessageBubble

ThreadDict = dict[str, Any]
MessageDict = dict[str, Any]


class ThreadList(ft.Column):
    def __init__(self, thread: ThreadDict, current_user_email: str) -> None:
        super().__init__()

        self.thread: ThreadDict = thread
        self.current_user_email: str = current_user_email

        self.spacing = 10
        self.expand = True

        # input box
        self.input_field = ft.TextField(
            hint_text="Type a reply...",
            border_radius=20,
            filled=True,
            bgcolor="white",
            dense=True,
            expand=True,
        )

        self._rebuild()

    # ------------------------------------------------------------------ #
    # load external API
    # ------------------------------------------------------------------ #
    def set_thread(self, thread: ThreadDict) -> None:
        # update current UI
        self.thread = thread
        self._rebuild()
        self.update()

    # ------------------------------------------------------------------ #
    # Internal helper: adapt backend message structure to the format used by MessageBubble
    # ------------------------------------------------------------------ #
    def _adapt_messages(self) -> list[MessageDict]:
        messages_raw = list(self.thread.get("messages", []))
        adapted: list[MessageDict] = []

        for m in messages_raw:
            sender = m.get("sender", {}) or {}
            sender_email = sender.get("email", "") or ""
            sender_name = (f"{sender.get('first_name', '')} {sender.get('last_name', '')}").strip()

            is_me = sender_email == self.current_user_email

            adapted.append(
                {
                    "id": m.get("id"),
                    "is_me": is_me,
                    "text": m.get("content", {}).get("body", ""),
                    "subject": m.get("subject", ""),
                    "sent_at": m.get("sent_at", ""),
                    "sender_name": sender_name,
                    "sender_email": sender_email,
                    "attachments": m.get("content", {}).get("attachments", []),
                }
            )

        return adapted

    # ------------------------------------------------------------------ #
    # rebuild the UI
    # ------------------------------------------------------------------ #
    def _rebuild(self) -> None:
        thread = self.thread
        messages_raw = list(thread.get("messages", []))

        # ---------- the information of top contact ---------- #
        if messages_raw:
            first_sender = messages_raw[0].get("sender", {}) or {}
            contact_name = (
                f"{first_sender.get('first_name', '')} {first_sender.get('last_name', '')}"
            ).strip()
            contact_email = first_sender.get("email", "") or ""
        else:
            contact_name = ""
            contact_email = ""

        header = ft.Row(
            controls=[
                ft.CircleAvatar(
                    content=ft.Text((contact_name[:2] or "?").upper()),
                    radius=20,
                ),
                ft.Column(
                    controls=[
                        ft.Text(contact_name or "Unknown", weight="bold"),
                        ft.Text(contact_email, size=12, color="gray"),
                    ],
                    spacing=2,
                ),
            ],
            alignment=ft.MainAxisAlignment.START,
            spacing=10,
        )

        # ---------- “Discussing email” 卡片 ---------- #
        title = str(thread.get("title", "")) or ""

        if messages_raw:
            last_msg = messages_raw[-1]
            last_summary = str(last_msg.get("content", {}).get("body", ""))
        else:
            last_summary = ""

        discussing_card = ft.Container(
            width=500,
            bgcolor="white",
            padding=15,
            border_radius=12,
            content=ft.Column(
                controls=[
                    ft.Text("Discussing email:", size=12, color="gray"),
                    ft.Text(title, weight="bold"),
                    ft.Text(
                        last_summary,
                        size=12,
                        color="gray",
                        max_lines=3,
                        overflow=ft.TextOverflow.ELLIPSIS,
                    ),
                ],
                spacing=4,
            ),
        )

        # ---------- message list ---------- #
        adapted_messages = self._adapt_messages()

        messages_column = ft.Column(
            controls=[MessageBubble(m) for m in adapted_messages],
            spacing=8,
            expand=True,
            scroll=ft.ScrollMode.AUTO,
        )

        # ---------- downside message input box ---------- #
        input_row = ft.Row(
            controls=[
                self.input_field,
                ft.IconButton(
                    icon=ft.Icons.SEND,
                    disabled=True,  # stake holder
                    tooltip="Send (coming soon)",
                ),
            ],
            spacing=10,
            alignment=ft.MainAxisAlignment.END,
        )

        # ---------- conbination of the whole layout ---------- #
        self.controls = [
            header,
            ft.Container(height=10),
            discussing_card,
            ft.Container(height=20),
            messages_column,
            ft.Container(height=8),
            input_row,
        ]


def main(page: ft.Page):
    demo_thread: ThreadDict = {
        "id": 1,
        "title": "Project Discussion",
        "messages": [
            # the object contact
            {
                "id": 101,
                "sender": {
                    "id": 1,
                    "first_name": "John",
                    "last_name": "Doe",
                    "email": "john.doe@example.com",
                },
                "subject": "Meeting Reminder",
                "content": {
                    "body": "Hello, how are you?",
                    "attachments": [],
                },
                "sent_at": "2024-05-30T10:15:30Z",
            },
            # me
            {
                "id": 102,
                "sender": {
                    "id": 2,
                    "first_name": "Me",
                    "last_name": "User",
                    "email": "me@example.com",
                },
                "subject": "Re: Meeting Reminder",
                "content": {
                    "body": "I'm good, thanks for asking!",
                    "attachments": [],
                },
                "sent_at": "2024-05-30T10:17:45Z",
            },
        ],
    }

    # current user is me
    current_user_email = "me@example.com"

    page.title = "Thread Conversation Test"
    page.padding = 20
    page.add(ThreadList(demo_thread, current_user_email))


if __name__ == "__main__":
    ft.app(target=main)

