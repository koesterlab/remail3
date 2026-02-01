# remail/client/widgets/dashboard/appointment_item.py
from __future__ import annotations

from datetime import datetime
from typing import Any

import flet as ft

from remail.controllers.dtos.conversations import ThreadPreviewDTO
from remail.controllers.dtos.user_dto import UserDTO

AppointmentDict = dict[str, Any]


class AppointmentItem(ft.Container):
    def __init__(self, thread: ThreadPreviewDTO, date: datetime, user: UserDTO) -> None:
        title: str = thread.title
        location: str = "Uni Duisburg-Essen (Placeholder for AI)"
        account_email: str = user.email
        time_label: str = date.strftime("%d. %B %Y")

        left_column = ft.Column(
            spacing=2,
            controls=[
                ft.Text(
                    title,
                    size=15,
                    weight=ft.FontWeight.W_600,
                    color=ft.Colors.ON_SURFACE,
                ),
                ft.Text(
                    location,
                    size=13,
                    color=ft.Colors.ON_SURFACE_VARIANT,
                ),
                ft.Row(
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
                    ],
                ),
            ],
        )

        super().__init__(
            bgcolor=ft.Colors.SURFACE,
            padding=ft.padding.all(14),
            border_radius=16,
            margin=ft.margin.only(bottom=10),
            content=ft.Row(
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                vertical_alignment=ft.CrossAxisAlignment.START,
                controls=[
                    left_column,
                    ft.Text(
                        time_label,
                        size=12,
                        color=ft.Colors.ON_SURFACE_VARIANT,
                    ),
                ],
            ),
        )
