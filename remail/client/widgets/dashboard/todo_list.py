# remail/client/widgets/dashboard/todo_list.py
from __future__ import annotations

from typing import Any

import flet as ft

from remail.client.widgets.dashboard.todo_item import TodoItem

TodoDict = dict[str, Any]


class TodoList(ft.Container):
    def __init__(self, todos: list[TodoDict]) -> None:
        self.todos = todos

        header_row = ft.Row(
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            controls=[
                ft.Column(
                    spacing=2,
                    controls=[
                        ft.Text(
                            "To Do",
                            size=18,
                            weight=ft.FontWeight.BOLD,
                            color=ft.Colors.ON_SURFACE,
                        ),
                        ft.Text(
                            f"{len(self.todos)} emails to answer",
                            size=13,
                            color=ft.Colors.ON_SURFACE_VARIANT,
                        ),
                    ],
                ),
            ],
        )

        items_column = ft.Column(
            spacing=6,
            controls=[TodoItem(t) for t in self.todos],
        )

        content_column = ft.Column(
            spacing=16,
            controls=[
                header_row,
                items_column,
            ],
        )

        super().__init__(
            bgcolor=None,
            # bgcolor=ft.Colors.SURFACE,
            padding=ft.padding.all(18),
            border_radius=24,
            expand=True,
            content=content_column,
        )
