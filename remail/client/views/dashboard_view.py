"""Dashboard view for the main application."""

from __future__ import annotations

import flet as ft

from remail.client.state.app_state import AppState
from remail.client.widgets.dashboard.dashboard_page import DashboardPage


def create_dashboard_view(page: ft.Page, app_state: AppState) -> ft.Container:
    """Create the dashboard view.

    Args:
        page: The Flet page object
        app_state: The application state

    Returns:
        A Container with the dashboard view
    """

    page.title = "Dashboard design"
    page.padding = 20

    # ------------------------------------------------------------------ #
    # Mock data
    # ------------------------------------------------------------------ #

    accounts = [
        {
            "email": "example1@email.com",
            "label": "Active",
            "color": ft.Colors.PRIMARY,
        },
        {
            "email": "example2@email.com",
            "label": "Active",
            "color": ft.Colors.PURPLE,
        },
    ]

    todos = [
        {
            "sender": "IWIS Sprachkurse",
            "subject": "C1 2-Kurs",
            "account_email": "example1@email.com",
            "time_label": "Heute 10:34 AM",
            "badge": "2 days",
        },
        {
            "sender": "Julia Müller",
            "subject": "Wissenschaftssprache: Lektion 2",
            "account_email": "example1@email.com",
            "time_label": "Mi 06:20 PM",
            "badge": "1 day",
        },
        {
            "sender": "Kevin Schott",
            "subject": "PIZZA-Event Reminder",
            "account_email": "example2@email.com",
            "time_label": "Di 03:31 PM",
            "badge": "3 days",
        },
        {
            "sender": "Sarah Johnson",
            "subject": "Project Update Request",
            "account_email": "example2@email.com",
            "time_label": "Di 02:15 PM",
            "badge": "1 day",
        },
    ]

    appointments = [
        {
            "title": "Team Meeting",
            "location": "Zoom",
            "account_email": "example2@email.com",
            "time_label": "Heute 15:00",
        },
        {
            "title": "German Language Class",
            "location": "Room 204",
            "account_email": "example1@email.com",
            "time_label": "Morgen 10:00",
        },
        {
            "title": "Doctor Appointment",
            "location": "Medical Center",
            "account_email": "example2@email.com",
            "time_label": "Freitag 14:30",
        },
    ]


    dashboard = DashboardPage(
        accounts=accounts,
        todos=todos,
        appointments=appointments,
    )

    return ft.Container(
        content=dashboard,
        expand=True,
    )
def main(page: ft.Page) -> None:
    app_state = AppState()

    page.bgcolor = ft.Colors.SURFACE
    page.scroll = ft.ScrollMode.AUTO

    root = create_dashboard_view(page, app_state)
    page.add(root)


if __name__ == "__main__":
    ft.app(target=main)