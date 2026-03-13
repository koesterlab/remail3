from collections.abc import Callable

import flet as ft

from remail.client.widgets.mail_selection.action import Action


class ActionPreview(ft.Container):
    def __init__(self, action: Action):
        super().__init__(
            on_click=action.on_executed,
            content=ft.Row(
                [
                    ft.CircleAvatar(
                        content=ft.Icon(ft.IconData(action.icon)),
                        color=action.color,
                        bgcolor=ft.Colors.WHITE,
                        radius=20,
                    ),
                    ft.Column(
                        [
                            ft.Row(
                                [
                                    ft.Text(action.title, weight=ft.FontWeight.BOLD),
                                ],
                                alignment=ft.MainAxisAlignment.START,
                            ),
                            ft.Row(
                                [ft.Text(action.secondary, size=12)],
                                alignment=ft.MainAxisAlignment.START,
                                spacing=6,
                            ),
                        ],
                        spacing=3,
                        alignment=ft.MainAxisAlignment.START,
                    ),
                    ft.Row([], expand=True, alignment=ft.MainAxisAlignment.END),
                ],
                spacing=12,
                alignment=ft.MainAxisAlignment.START,
            ),
            padding=12,
        )
