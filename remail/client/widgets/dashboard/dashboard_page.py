# remail/client/widgets/dashboard/dashboard_page.py

from __future__ import annotations

from typing import Any

import flet as ft

from remail.client.widgets.dashboard.account_card import AccountCard
from remail.client.widgets.dashboard.todo_list import TodoList
from remail.client.widgets.dashboard.appointments_list import AppointmentsList


AccountDict = dict[str, Any]
TodoDict = dict[str, Any]
AppointmentDict = dict[str, Any]


class DashboardPage(ft.Column):

    def __init__(
        self,
        accounts: list[AccountDict],
        todos: list[TodoDict],
        appointments: list[AppointmentDict],
    ) -> None:
        super().__init__(expand=True, spacing=20)
        self.accounts = accounts
        self.todos = todos
        self.appointments = appointments
        self._rebuild()

    def _rebuild(self) -> None:
        header = ft.Text(
            "Good evening, Leader one!",
            size=26,
            weight=ft.FontWeight.BOLD,
            color=ft.Colors.ON_SURFACE,
        )

        sub_header = ft.Text(
            "Here is the summary of your email system:",
            size=16,
            color=ft.Colors.ON_SURFACE_VARIANT,
        )


        accounts_card = ft.Container(
            bgcolor=ft.Colors.WHITE,
            padding=ft.padding.all(16),
            border_radius=24,
            content=ft.Row(
                controls=[AccountCard(acc) for acc in self.accounts],
                spacing=20,
            ),
        )

        content_card = ft.Container(
            bgcolor=ft.Colors.WHITE,
            padding=ft.padding.all(18),
            border_radius=24,
            content=ft.Row(
                expand=True,
                spacing=20,
                alignment=ft.MainAxisAlignment.START,
                vertical_alignment=ft.CrossAxisAlignment.START,
                controls=[
                    ft.Container(
                        TodoList(self.todos),
                        expand=1,
                    ),
                    ft.Container(
                        AppointmentsList(self.appointments),
                        expand=1,
                    ),
                ],
            ),
        )


        inner_column = ft.Column(
            spacing=20,
            controls=[
                header,
                sub_header,
                accounts_card,
                content_card,
            ],
        )

        self.controls = [
            ft.Container(
                expand=True,
                alignment=ft.alignment.top_center,
                bgcolor=ft.Colors.SURFACE, 
                padding=ft.padding.symmetric(vertical=20, horizontal=0),
                content=ft.Container(
                    width=1000,
                    padding=ft.padding.symmetric(horizontal=20),
                    content=inner_column,
                ),
            )
        ]
