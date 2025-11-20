from __future__ import annotations

from datetime import datetime
import flet as ft

from .conversation_list import ConversationList, ConversationDict
from .conversation_view import ConversationView
from .sidebar_nav import SidebarNav
from .top_bar import TopBar


class ConversationsWidget:
    def __init__(self) -> None:
        self._conversations = self._make_mock_data()
        self._selected = self._conversations[0]

    def _make_mock_data(self) -> list[ConversationDict]:
        base_messages = [
            {
                "sender_name": "Me",
                "is_me": True,
                "text": "Hello! I saw your email about the C1 course.",
                "sent_at": datetime.now(),
            },
            {
                "sender_name": "IWiS Sprachkurse",
                "is_me": False,
                "text": "Yes, thank you for reaching out! Do you have any questions?",
                "sent_at": datetime.now(),
            },
            {
                "sender_name": "Me",
                "is_me": True,
                "text": "When does the course start exactly?",
                "sent_at": datetime.now(),
            },
            {
                "sender_name": "IWiS Sprachkurse",
                "is_me": False,
                "text": "The course starts next Monday at 9:00 AM...",
                "sent_at": datetime.now(),
            },
        ]

        return [
            {
                "id": 1,
                "contact_name": "IWiS Sprachkurse",
                "contact_email": "iwis@university.de",
                "last_summary": "Information about the upcoming C1 German language course...",
                "tag": "C 1 2-Kurs",
                "messages": base_messages,
            },
            {
                "id": 2,
                "contact_name": "Julia Müller",
                "contact_email": "julia.mueller@example.com",
                "last_summary": "Can we discuss Lektion 2 tomorrow?",
                "tag": "Wissenschaftssprache: Lektion 2",
                "messages": [
                    {
                        "sender_name": "Julia Müller",
                        "is_me": False,
                        "text": "Can we discuss Lektion 2 tomorrow?",
                        "sent_at": datetime.now(),
                    },
                    {
                        "sender_name": "Me",
                        "is_me": True,
                        "text": "Sure, what time works for you?",
                        "sent_at": datetime.now(),
                    },
                ],
            },
            {
                "id": 3,
                "contact_name": "Kevin Schott",
                "contact_email": "kevin.schott@example.com",
                "last_summary": "Looking forward to the PIZZA event!",
                "tag": "PIZZA-Event Reminder",
                "messages": [
                    {
                        "sender_name": "Kevin Schott",
                        "is_me": False,
                        "text": "Looking forward to the PIZZA event!",
                        "sent_at": datetime.now(),
                    },
                    {
                        "sender_name": "Me",
                        "is_me": True,
                        "text": "Same here 😄 See you there!",
                        "sent_at": datetime.now(),
                    },
                ],
            },
            {
                "id": 4,
                "contact_name": "Prof. Schmidt",
                "contact_email": "prof.schmidt@example.com",
                "last_summary": "I received your assignment submission.",
                "tag": "Re: Assignment Submission",
                "messages": [
                    {
                        "sender_name": "Prof. Schmidt",
                        "is_me": False,
                        "text": "I received your assignment submission. We will review it this week.",
                        "sent_at": datetime.now(),
                    },
                    {
                        "sender_name": "Me",
                        "is_me": True,
                        "text": "Thank you, I look forward to your feedback.",
                        "sent_at": datetime.now(),
                    },
                ],
            },
        ]

    def build(self) -> ft.Control:
        conversation_view = ConversationView(self._selected)

        def on_select(conv: ConversationDict) -> None:
            conversation_view.set_conversation(conv)

        conv_list = ConversationList(self._conversations, on_select)
        sidebar = SidebarNav()
        top_bar = TopBar()

        floating_compose = ft.FloatingActionButton(icon=ft.icons.CREATE)

        layout = ft.Stack(
            controls=[
                ft.Column(
                    expand=True,
                    controls=[
                        top_bar,
                        ft.Row(
                            expand=True,
                            vertical_alignment=ft.CrossAxisAlignment.START,
                            controls=[
                                ft.Container(
                                    width=160,
                                    #bgcolor="#0f172a",
                                    padding=ft.padding.only(
                                        top=20,
                                        left=10,
                                        right=10,
                                    ),
                                    content=sidebar,
                                ),
                                ft.Container(
                                    width=260,
                                    padding=ft.padding.only(
                                        top=4,
                                        left=10,
                                        right=10,
                                        bottom=10,
                                    ),
                                    content=conv_list,
                                ),
                                ft.Container(
                                    expand=True,
                                    padding=ft.padding.only(
                                        top=16,
                                        left=20,
                                        right=20,
                                        bottom=20,
                                    ),
                                    content=conversation_view,
                                ),
                            ],
                        ),
                    ],
                ),
                ft.Container(
                    right=30,
                    bottom=30,
                    content=floating_compose,
                ),
            ]
        )

        return layout


def main(page: ft.Page) -> None:
    page.title = "ReMail Conversations (Standalone)"
    page.bgcolor = "#f3f4f6"
    page.padding = 10

    widget = ConversationsWidget()
    page.add(widget.build())


if __name__ == "__main__":
    ft.app(target=main)
