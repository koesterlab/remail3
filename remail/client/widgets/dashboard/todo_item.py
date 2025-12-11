# remail/client/widgets/dashboard/todo_item.py
from __future__ import annotations

from typing import Any

import flet as ft

TodoDict = dict[str, Any]


class TodoItem(ft.Container):


    def __init__(self, todo: TodoDict) -> None:
        sender: str = todo.get("sender", "")
        subject: str = todo.get("subject", "")
        account_email: str = todo.get("account_email", "")
        time_label: str = todo.get("time_label", "")
        badge: str = todo.get("badge", "")


        top_row = ft.Row(
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            controls=[
                ft.Column(
                    spacing=2,
                    controls=[
                        ft.Text(
                            sender,
                            size=15,
                            weight=ft.FontWeight.W_600,
                            color=ft.Colors.ON_SURFACE,
                        ),
                        ft.Text(
                            subject,
                            size=13,
                            color=ft.Colors.ON_SURFACE_VARIANT,
                        ),
                    ],
                ),
                ft.Text(
                    badge,
                    size=12,
                    weight=ft.FontWeight.W_500,
                    color=ft.Colors.ERROR,
                ),
            ],
        )


        meta_row = ft.Row(
            spacing=6,
            controls=[
                ft.Icon(
                    ft.Icons.EMAIL_OUTLINED,
                    size=14,
                    color=ft.Colors.ON_SURFACE_VARIANT,
                ),
                ft.Text(
                    account_email,
                    size=12,
                    color=ft.Colors.ON_SURFACE_VARIANT,
                ),
                ft.Text(
                    "•",
                    size=12,
                    color=ft.Colors.ON_SURFACE_VARIANT,
                ),
                ft.Text(
                    time_label,
                    size=12,
                    color=ft.Colors.ON_SURFACE_VARIANT,
                ),
            ],
        )


        quick_reply = ft.Container(
            margin=ft.margin.only(top=8),
            padding=ft.padding.symmetric(horizontal=12, vertical=8),
            border_radius=20,
            bgcolor=ft.Colors.SURFACE,
            content=ft.Row(
                alignment=ft.MainAxisAlignment.START,
                spacing=8,
                controls=[
                    ft.Icon(
                        ft.Icons.CHAT_BUBBLE_OUTLINE,
                        size=16,
                        color=ft.Colors.ON_SURFACE_VARIANT,
                    ),
                    ft.Text(
                        "Quick Reply",
                        size=13,
                        weight=ft.FontWeight.W_500,
                        color=ft.Colors.ON_SURFACE,
                    ),
                ],
            ),
        )

        content_column = ft.Column(
            spacing=6,
            controls=[
                top_row,
                meta_row,
                quick_reply,
            ],
        )

        super().__init__(
            bgcolor=ft.Colors.SURFACE,
            padding=ft.padding.all(14),
            border_radius=16,
            margin=ft.margin.only(bottom=12),
            content=content_column,
        )

