import flet as ft


def create_connected_email_accounts():
    def add_account_click(e):
        print("Add account clicked")

    return ft.Container(
        ft.Column(
            [
                ft.Text("Connected Email Accounts", weight=ft.FontWeight.BOLD),
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
            ]
        ),
        padding=20,
        border_radius=10,
        alignment=ft.alignment.center_left,
    )
