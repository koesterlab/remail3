# remail/client/widgets/dashboard/appointment_item.py
from __future__ import annotations

from typing import Any

import flet as ft

AppointmentDict = dict[str, Any]


class AppointmentItem(ft.Container):
    def __init__(self, app: AppointmentDict) -> None:
        title: str = app.get("title", "")
        location: str = app.get("location", "")
        account_email: str = app.get("account_email", "")
        time_label: str = app.get("time_label", "")

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
