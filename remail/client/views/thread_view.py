"""Thread view for the main application."""

from __future__ import annotations

import flet as ft

from remail.client.state.app_state import AppState
from remail.client.widgets.thread_widget import ThreadDict, ThreadList


def create_thread_view(page: ft.Page, app_state: AppState) -> ft.Container:
    """Create the thread view.

    Args:
        page: The Flet page object
        app_state: The application state

    Returns:
        A Container with the thread view
    """

    page.title = "Remail 2.0 - Thread"
    page.padding = 20

    # ------------------------------------------------------------------ #
    # MOCk Data

    # ------------------------------------------------------------------ #
    demo_thread: ThreadDict = {
        "id": 1,
        "title": "Project Discussion",
        "messages": [
            # another side
            {
                "id": 101,
                "sender": {
                    "id": 1,
                    "first_name": "John",
                    "last_name": "Doe",
                    "email": "john.doe@example.com",
                },
                "subject": "Meeting Reminder",
                "content": {
                    "body": "Hello, how are you?",
                    "attachments": [],
                },
                "sent_at": "2024-05-30T10:15:30Z",
            },
            # my side
            {
                "id": 102,
                "sender": {
                    "id": 2,
                    "first_name": "Me",
                    "last_name": "User",
                    "email": "me@example.com",
                },
                "subject": "Re: Meeting Reminder",
                "content": {
                    "body": "I'm good, thanks for asking!",
                    "attachments": [],
                },
                "sent_at": "2024-05-30T10:17:45Z",
            },
        ],
    }

    # current mock email
    current_user_email = "me@example.com"

    # create thread widget
    thread_widget = ThreadList(demo_thread, current_user_email)

    return ft.Container(
        content=thread_widget,
        expand=True,
    )
