# remail/client/widgets/dashboard/appointments_list.py
from __future__ import annotations

from typing import Any

import flet as ft

from remail.client.widgets.dashboard.appointment_item import AppointmentItem

AppointmentDict = dict[str, Any]


class AppointmentsList(ft.Container):
    def __init__(self, appointments: list[AppointmentDict]) -> None:
        self.appointments = appointments

        header_row = ft.Row(
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            controls=[
                ft.Column(
                    spacing=2,
                    controls=[
                        ft.Text(
                            "Appointments",
                            size=18,
                            weight=ft.FontWeight.BOLD,
                            color=ft.Colors.ON_SURFACE,
                        ),
                        ft.Text(
                            f"{len(self.appointments)} upcoming",
                            size=13,
                            color=ft.Colors.ON_SURFACE_VARIANT,
                        ),
                    ],
                ),
            ],
        )

        items_column = ft.Column(
            spacing=6,
            controls=[AppointmentItem(a) for a in self.appointments],
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
            padding=0,
            border_radius=0,
            expand=True,
            content=content_column,
        )
