import flet as ft

from remail.client.state.app_state import AppState
from remail.client.views.settings.appearance_view import appearance_view


def settings_view(page: ft.Page, app_state: AppState) -> ft.Container:
    """Create the main settings view with navigation and child views."""

    # State to track current view
    current_view = {"name": "appearance"}

    # Create a container for the content that will change
    content_container = ft.Container()

    def load_view(view_name: str):
        """Load and display the specified view."""
        current_view["name"] = view_name

        if view_name == "appearance":
            content_container.content = appearance_view(page, app_state)
        # Add more views here as needed
        # elif view_name == "account":
        #     content_container.content = account_view(page, app_state)

        page.update()

    def create_nav_item(label: str, view_name: str) -> ft.TextButton:
        """Create a navigation item for the settings menu."""

        def on_click(e):
            load_view(view_name)

        return ft.TextButton(
            text=label,
            on_click=on_click,
        )

    # Navigation menu
    nav_menu = ft.Container(
        ft.Column(
            [
                ft.Text("Settings", size=24, weight=ft.FontWeight.BOLD),
                ft.Divider(height=2),
                create_nav_item("Appearance", "appearance"),
                # Add more navigation items here
                # create_nav_item("Account", "account"),
                # create_nav_item("Notifications", "notifications"),
            ],
            spacing=5,
        ),
        width=200,
        padding=10,
    )

    # Load initial view
    load_view("appearance")

    # Main layout with navigation on left and content on right
    return ft.Container(
        ft.Row(
            [
                nav_menu,
                ft.VerticalDivider(width=1),
                ft.Container(
                    content_container,
                    expand=True,
                ),
            ],
            expand=True,
        ),
        expand=True,
    )
