import flet as ft

from remail.client.state.app_state import AppState


def create_email_accounts_view(page: ft.Page, app_state: AppState) -> ft.Container:
    """Create the email accounts settings view."""

    def add_account_click(e):
        # TODO: Implement add account functionality
        print("Add account clicked")

    return ft.Container(
        ft.Column(
            [
                ft.Text("Email Accounts", size=18, weight=ft.FontWeight.BOLD),
                ft.Text("Manage your email accounts"),
                ft.Divider(height=2, color=ft.Colors.BLACK),
                ft.Text("No accounts connected yet"),
                ft.Container(
                    ft.OutlinedButton(
                        "Add Email Account",
                        icon="add",
                        on_click=add_account_click,
                    ),
                    alignment=ft.alignment.center,
                    margin=ft.margin.only(top=20),
                ),
            ],
            spacing=15,
        ),
        padding=20,
        border_radius=10,
        alignment=ft.alignment.center_left,
    )
