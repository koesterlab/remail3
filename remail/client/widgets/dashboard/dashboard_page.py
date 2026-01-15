from __future__ import annotations

from datetime import datetime
from typing import Any

import flet as ft

from remail.client.widgets.dashboard.account_card import AccountCard
from remail.client.widgets.dashboard.appointments_list import AppointmentsList
from remail.client.widgets.dashboard.todo_list import TodoList


AccountDict = dict[str, Any]
TodoDict = dict[str, Any]
AppointmentDict = dict[str, Any]


def _time_greeting(now: datetime | None = None) -> str:
    """Return 'Good morning/afternoon/evening' based on local time."""
    now = now or datetime.now()
    hour = now.hour
    if hour < 12:
        return "Good morning"
    if hour < 18:
        return "Good afternoon"
    return "Good evening"


def _display_name_from_account(account: AccountDict | None) -> str:
    """
    Try to get a nice display name from the first account.
    Priority:
      1) explicit account['name'] (if present)
      2) infer from email local-part
      3) fallback to 'there'
    """
    if not account:
        return "there"

    # 1) Prefer an explicit name if your account dict contains one
    name = str(account.get("name", "")).strip()
    if name:
        return name

    # 2) Fallback: infer from email
    email = str(account.get("email", "")).strip()
    if not email:
        return "there"

    local = email.split("@", 1)[0]
    # Turn separators into spaces
    local = local.replace(".", " ").replace("_", " ").replace("-", " ").strip()
    if not local:
        return "there"

    # Title-case words (e.g. "julia mueller" -> "Julia Mueller")
    return " ".join(w.capitalize() for w in local.split())


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
        # Compute greeting + name dynamically
        greeting = _time_greeting()
        first_name = _display_name_from_account(self.accounts[0] if self.accounts else None)

        header = ft.Text(
            f"{greeting}, {first_name}!",
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
