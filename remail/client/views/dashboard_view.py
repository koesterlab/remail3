"""Dashboard view for the main application."""

from __future__ import annotations

from datetime import datetime, timedelta

import flet as ft

from remail.client.state.app_state import AppState
from remail.client.widgets.dashboard.dashboard_page import DashboardPage


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
    """Return compact badges like '2h', '1d', '-3h'."""
    delta = dt - now
    seconds = int(delta.total_seconds())
    past = seconds < 0
    seconds = abs(seconds)

    minutes = seconds // 60
    hours = minutes // 60
    days = hours // 24

    if days >= 1:
        value = f"{days}d"
    elif hours >= 1:
        value = f"{hours}h"
    else:
        value = f"{max(1, minutes)}m"

    return f"-{value}" if past else value


# ------------------------------------------------------------------ #
# Dashboard view
# ------------------------------------------------------------------ #

def create_dashboard_view(page: ft.Page, app_state: AppState) -> ft.Container:
    """Create the dashboard view."""

    page.title = "Dashboard"
    page.padding = 20

    now = datetime.now()

    # ------------------------------------------------------------------ #
    # Mock accounts
    # ------------------------------------------------------------------ #

    accounts = [
        {
            "email": "ude-1729267167@uni-due.de",
            "label": "Active",
            "color": ft.Colors.PRIMARY,
        },
        {
            "email": "example2@email.com",
            "label": "Active",
            "color": ft.Colors.PURPLE,
        },
    ]

    # ------------------------------------------------------------------ #
    # Mock todos (emails / tasks)
    # ------------------------------------------------------------------ #

    todo_times = [
        now.replace(hour=10, minute=34, second=0, microsecond=0),
        (now - timedelta(days=1)).replace(hour=18, minute=20, second=0, microsecond=0),
        (now - timedelta(days=2)).replace(hour=15, minute=31, second=0, microsecond=0),
        (now - timedelta(days=3)).replace(hour=14, minute=15, second=0, microsecond=0),
    ]

    todos_raw = [
        ("IWIS Sprachkurse", "C1 2-Kurs", "example1@email.com"),
        ("Julia Müller", "Wissenschaftssprache: Lektion 2", "example1@email.com"),
        ("Kevin Schott", "PIZZA-Event Reminder", "example2@email.com"),
        ("Sarah Johnson", "Project Update Request", "example2@email.com"),
    ]

    todos = []
    for (sender, subject, acc), dt in zip(todos_raw, todo_times, strict=False):
        todos.append(
            {
                "sender": sender,
                "subject": subject,
                "account_email": acc,
                "time_label": fmt_time_label(dt, now),
                "badge": fmt_badge(dt, now),
            }
        )

    # ------------------------------------------------------------------ #
    # Mock appointments
    # ------------------------------------------------------------------ #

    appt_times = [
        now.replace(hour=15, minute=0, second=0, microsecond=0),
        (now + timedelta(days=1)).replace(hour=10, minute=0, second=0, microsecond=0),
        (now + timedelta(days=3)).replace(hour=14, minute=30, second=0, microsecond=0),
    ]

    appointments_raw = [
        ("Team Meeting", "Zoom", "example2@email.com"),
        ("German Language Class", "Room 204", "example1@email.com"),
        ("Doctor Appointment", "Medical Center", "example2@email.com"),
    ]

    appointments = []
    for (title, location, acc), dt in zip(appointments_raw, appt_times, strict=False):
        appointments.append(
            {
                "title": title,
                "location": location,
                "account_email": acc,
                "time_label": fmt_time_label(dt, now),
            }
        )

    # ------------------------------------------------------------------ #
    # Build dashboard
    # ------------------------------------------------------------------ #

    dashboard = DashboardPage(
        accounts=accounts,
        todos=todos,
        appointments=appointments,
    )

    return ft.Container(
        content=dashboard,
        expand=True,
    )


# ------------------------------------------------------------------ #
# Standalone entry point (for preview)
# ------------------------------------------------------------------ #

def main(page: ft.Page) -> None:
    app_state = AppState()

    page.bgcolor = ft.Colors.SURFACE
    page.scroll = ft.ScrollMode.AUTO

    root = create_dashboard_view(page, app_state)
    page.add(root)


if __name__ == "__main__":
    ft.app(target=main)
