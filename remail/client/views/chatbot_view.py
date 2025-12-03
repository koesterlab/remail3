"""Chatbot view for the main application."""

import flet as ft

from remail.client.state.app_state import AppState
from remail.client.widgets.chatbot.chatbot import create_chatbot


def create_chatbot_view(page: ft.Page, app_state: AppState) -> ft.Container:
    """Create the chatbot view.

    Args:
        page: The Flet page object
        app_state: The application state

    Returns:
        A Container with the chatbot view
    """

    page.title = "Remail 2.0 - Chatbot"
    page.padding = 20

    # Create the chatbot widget
    chatbot = create_chatbot()

    return ft.Container(
        content=chatbot,
        expand=True,
    )
