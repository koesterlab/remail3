# remail/client/views/dashboard_view.py
"""Dashboard view for the main application (DB-backed)."""

from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any

import flet as ft

from remail.client.state.app_state import AppState
from remail.client.widgets.dashboard.dashboard_page import DashboardPage
from remail.controllers.dtos.user_dto import UserDTO
from remail.interfaces.email.services.dashboard_service import DashboardService
from remail.interfaces.email.services.user_service import UserService

# ------------------------------------------------------------------ #
# Helper functions for realistic time labels
# ------------------------------------------------------------------ #

WEEKDAYS_DE = ["Mo", "Di", "Mi", "Do", "Fr", "Sa", "So"]


def fmt_time_label(dt: datetime, now: datetime) -> str:
    """Return labels like 'today 10:34', 'yesterday 18:20', 'Mi 06:20'."""
    today = now.date()
    d = dt.date()

    if d == today:
        prefix = "today"
    elif d == today - timedelta(days=1):
        prefix = "yesterday"
    elif d == today + timedelta(days=1):
        prefix = "tomorrow"
    else:
        prefix = WEEKDAYS_DE[dt.weekday()]

    return f"{prefix} {dt:%H:%M}"


def fmt_badge(dt: datetime, now: datetime) -> str:
    """
    Return compact badges like '2h', '1d' (always "time ago").

    Why:
    - Seed/test data or clock skews can accidentally create future timestamps.
    - For UI, it is nicer to always show "age" rather than negative values.
    """
    seconds = int((now - dt).total_seconds())
    seconds = max(0, seconds)

    minutes = seconds // 60
    hours = minutes // 60
    days = hours // 24

    if days >= 1:
        return f"{days}d"
    if hours >= 1:
        return f"{hours}h"
    return f"{max(1, minutes)}m"


# ------------------------------------------------------------------ #
# DB → Dashboard data mappers
# ------------------------------------------------------------------ #

AccountDict = dict[str, Any]
TodoDict = dict[str, Any]
AppointmentDict = dict[str, Any]


def _user_email_label(u: UserDTO) -> str:
    """
    UI display label for a user account.

    Notes:
    - In the current DTO, we don't have a dedicated `email` field.
    - `username` is often the email already; if not, we compose `username@host`.
    """
    if "@" in u.username:
        return u.username
    return f"{u.username}@{u.host}"


def _build_accounts() -> list[AccountDict]:
    """
    Build account cards from DB users.
    """
    users = UserService.get_all_users()

    palette = [
        ft.Colors.PRIMARY,
        ft.Colors.PURPLE,
        ft.Colors.TEAL,
        ft.Colors.ORANGE,
    ]

    accounts: list[AccountDict] = []
    for i, u in enumerate(users):
        accounts.append(
            {
                "email": _user_email_label(u),
                "name": u.name,
                "label": "Active",
                "color": palette[i % len(palette)],
            }
        )
    return accounts


def _get_user_email(user_id: int) -> str:
    """Helper to map user_id -> user email for UI labels."""
    for u in UserService.get_all_users():
        if u.id == user_id:
            return _user_email_label(u)
    return ""


def _load_todos_for_user(user_id: int, now: datetime, limit: int = 6) -> list[TodoDict]:
    """
    Map recent emails to "To Do" items.

    Current assumption for UI testing:
    - Recent emails are considered items that may need attention/reply.
    """
    rows = DashboardService.get_recent_emails_for_user(user_id=user_id, limit=limit)
    account_email = _get_user_email(user_id)

    todos: list[TodoDict] = []
    for email, sender in rows:
        todos.append(
            {
                "sender": sender.name,
                "subject": email.subject,
                "account_email": account_email,
                "time_label": fmt_time_label(email.sent_at, now),
                "badge": fmt_badge(email.sent_at, now),
            }
        )

    return todos


def _load_appointments_for_user(
    user_id: int,
    now: datetime,
    limit: int = 3,
) -> list[AppointmentDict]:
    """
    Temporary appointments for UI testing:
    - Just show the most recent emails as appointment items.
    - This guarantees the appointments panel has content without adding new DB tables.
    """
    rows = DashboardService.get_recent_appointment_items_for_user(user_id=user_id, limit=limit)
    account_email = _get_user_email(user_id)

    appointments: list[AppointmentDict] = []
    for email, sender in rows:
        appointments.append(
            {
                "title": email.subject,
                "location": f"From: {sender.name}",  # lightweight placeholder
                "account_email": account_email,
                "time_label": fmt_time_label(email.sent_at, now),
            }
        )

    return appointments


# ------------------------------------------------------------------ #
# Dashboard view
# ------------------------------------------------------------------ #


def create_dashboard_view(
    page: ft.Page,
    app_state: AppState,
    active_user_id: int,
) -> ft.Container:
    """Create the dashboard view (data from DB)."""
    # page.title = "Dashboard"
    page.padding = 20

    now = datetime.now()

    accounts = _build_accounts()
    todos = _load_todos_for_user(active_user_id, now, limit=6)
    appointments = _load_appointments_for_user(active_user_id, now, limit=3)

    dashboard = DashboardPage(
        accounts=accounts,
        todos=todos,
        appointments=appointments,
    )

    return ft.Container(content=dashboard, expand=True)


# ------------------------------------------------------------------ #
# Standalone entry point (for preview)
# ------------------------------------------------------------------ #


def main(page: ft.Page) -> None:
    app_state = AppState()

    page.bgcolor = ft.Colors.SURFACE
    page.scroll = ft.ScrollMode.AUTO

    users = UserService.get_all_users()
    active_user_id = users[0].id if users else 0

    root = create_dashboard_view(page, app_state, active_user_id)
    page.add(root)


if __name__ == "__main__":
    ft.app(target=main)
