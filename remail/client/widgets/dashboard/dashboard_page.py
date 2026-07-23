from __future__ import annotations

import logging
from datetime import datetime
from typing import Any

import flet as ft

from remail.client.state import MainAppState, MainAppStateProperties
from remail.client.widgets.dashboard.account_card import AccountCard
from remail.client.widgets.dashboard.appointments_list import AppointmentsList
from remail.client.widgets.dashboard.todo_list import TodoList
from remail.controllers.dtos.user_dto import UserDTO
from remail.enums import SettingsSubView

AccountDict = dict[str, Any]
TodoDict = dict[str, Any]
AppointmentDict = dict[str, Any]

_logger = logging.getLogger(__name__)


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
        state: MainAppState,
    ) -> None:
        super().__init__(expand=True, spacing=20)
        self.state = state
        self.accounts = list(self.state.account_controllers.values())
        state.register_observer(MainAppStateProperties.ACTIVE_USER, self.on_user_change)
        self._rebuild()

    def on_user_change(self, acc: UserDTO):
        from remail.utils.timer import Timer

        new_accounts = list(self.state.account_controllers.values())
        if new_accounts != self.accounts:
            self.accounts = new_accounts
            _logger.info("DashboardPage: rebuilding...")
            t = Timer()
            self._rebuild()
            _logger.info("DashboardPage: _rebuild done. (%s)", t.elapsed())
            try:
                t2 = Timer()
                self.update()
                _logger.info("DashboardPage: update done. (%s)", t2.elapsed())
            except Exception:  # nosec B110
                pass
            return
        if not hasattr(self, "dropdown") or self.dropdown is None:
            return
        if acc is not None:
            self.dropdown.value = str(acc.id)
            try:
                self.dropdown.update()
            except Exception:  # nosec B110
                pass

    def refresh(self) -> None:
        """Rebuild the dashboard from the current DB state.

        Called when the dashboard is (re)opened so background changes such as
        auto-tagging show up. Reuses this instance, so no extra observer is
        registered; it just reconstructs the content (todo list, appointments).
        """
        self.accounts = list(self.state.account_controllers.values())
        self._rebuild()
        try:
            self.update()
        except Exception:  # nosec B110
            pass

    def _open_attachments(self, _: object) -> None:
        self.state.set(MainAppStateProperties.ACTIVE_THREAD, None)
        self.state.set(MainAppStateProperties.ACTIVE_ATTACHMENTS, True)

    def _rebuild(self) -> None:
        # Compute greeting + name dynamically
        greeting = _time_greeting()
        if not self.accounts:
            return  # todo show message
        first_name = self.accounts[0].get_user().name.split()[0]

        self.dropdown = ft.Dropdown(
            value=str(self.state.get(MainAppStateProperties.ACTIVE_USER).id)
            if self.state.get(MainAppStateProperties.ACTIVE_USER)
            else None,
            text_size=10,
            width=250,
            border_radius=24,
            options=[
                ft.DropdownOption(
                    content=AccountCard(acc), key=str(acc.id), text=f"{acc.name} <{acc.email}>"
                )
                for acc in [c.get_user() for c in self.accounts]
            ],
            on_select=lambda user_id: self.state.set(
                MainAppStateProperties.ACTIVE_USER,
                [a for a in self.accounts if str(a.user_id) == str(user_id.data)][0].get_user(),
            ),
        )

        header = ft.Container(
            ft.Row(
                [
                    ft.Text(
                        f"{greeting}, {first_name}!",
                        size=26,
                        weight=ft.FontWeight.BOLD,
                        color=ft.Colors.ON_SURFACE,
                    ),
                    ft.Column(
                        [
                            self.dropdown,
                            ft.Row(
                                [
                                    ft.IconButton(
                                        icon_color=ft.Colors.ON_SURFACE_VARIANT,
                                        icon=ft.Icons.ATTACH_FILE,
                                        tooltip="Attachments",
                                        on_click=self._open_attachments,
                                    ),
                                    ft.IconButton(
                                        icon_color=ft.Colors.ON_SURFACE_VARIANT,
                                        icon=ft.Icons.SETTINGS,
                                        tooltip="Settings",
                                        on_click=lambda _: self.state.set(
                                            MainAppStateProperties.ACTIVE_SETTINGS,
                                            SettingsSubView.APPEARANCE,
                                        ),
                                    ),
                                ],
                                spacing=0,
                                alignment=ft.MainAxisAlignment.END,
                            ),
                        ],
                        horizontal_alignment=ft.CrossAxisAlignment.END,
                    ),
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                expand=True,
                vertical_alignment=ft.CrossAxisAlignment.END,
            )
        )

        sub_header = ft.Text(
            """
This should be the summary of the emails since the last login. It could for example be a hint for very important message from the supervisor, a summary of multiple client complains, a relationship between multiple mails (maybe even links to the threads) or a warning for a failed email sending.
            """,
            size=16,
            color=ft.Colors.ON_SURFACE_VARIANT,
            selectable=True,
        )

        content_card = ft.Container(
            bgcolor=ft.Colors.SECONDARY_CONTAINER,
            border_radius=24,
            expand=True,
            content=ft.Row(
                expand=True,
                spacing=20,
                alignment=ft.MainAxisAlignment.START,
                vertical_alignment=ft.CrossAxisAlignment.START,
                controls=[
                    ft.Container(
                        TodoList(self.state),
                        expand=1,
                    ),
                    ft.Container(
                        AppointmentsList(self.state),
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
                content_card,
            ],
        )

        self.controls = [
            ft.Container(
                expand=True,
                alignment=ft.Alignment.TOP_CENTER,
                bgcolor=ft.Colors.SURFACE,
                content=ft.Container(
                    expand=True,
                    padding=ft.Padding.symmetric(horizontal=10),
                    content=inner_column,
                ),
            )
        ]
