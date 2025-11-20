from __future__ import annotations

from collections.abc import Callable
from typing import Any

import flet as ft

ConversationDict = dict[str, Any]


class ConversationList(ft.Column):
    """
    Left-hand conversation list.
    `on_select` is triggered when an item is clicked, with the conversation dict as the argument.
    """

    def __init__(
        self,
        conversations: list[ConversationDict],
        on_select: Callable[[ConversationDict], None],
    ) -> None:
        super().__init__()
        self.conversations = conversations
        self.on_select = on_select
        self.expand = True
        self.spacing = 10

        self._search = ft.TextField(
            hint_text="Search contacts, groups, topics...",
            border_radius=20,
            prefix_icon=ft.icons.SEARCH,
            dense=True,
        )

        self._list_view = ft.ListView(expand=True, spacing=6)
        self._rebuild_items()

        self.controls = [
            self._search,
            self._list_view,
        ]

    def set_conversations(self, conversations: list[ConversationDict]) -> None:
        self.conversations = conversations
        self._rebuild_items()
        self.update()

    def _rebuild_items(self) -> None:
        items: list[ft.Control] = []
        for conv in self.conversations:
            items.append(self._build_item(conv))
        self._list_view.controls = items

    def _build_item(self, conv: ConversationDict) -> ft.Control:
        contact_name = str(conv.get("contact_name", ""))
        last_summary = str(conv.get("last_summary", ""))
        tag = conv.get("tag") or ""

        item = ft.Container(
            on_click=lambda e, c=conv: self.on_select(c),
            padding=10,
            bgcolor="white",
            border_radius=8,
            content=ft.Row(
                spacing=10,
                controls=[
                    ft.CircleAvatar(content=ft.Text(contact_name[:2] or "?")),
                    ft.Column(
                        spacing=2,
                        controls=[
                            ft.Text(contact_name, weight="bold"),
                            ft.Text(last_summary, size=12, color="gray"),
                            ft.Text(tag, size=11, color="#0069ff"),
                        ],
                    ),
                ],
            ),
        )

        def on_hover(e: Any) -> None:
            item.bgcolor = "#e5e7eb" if e.data == "true" else "white"
            item.update()

        item.on_hover = on_hover

        return item
