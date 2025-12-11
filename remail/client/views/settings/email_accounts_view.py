import flet as ft

from remail.client.state.app_state import AppState
from remail.controllers.email_controller import EmailController


def create_email_accounts_view(page: ft.Page, app_state: AppState) -> ft.Container:
    """Create the email accounts settings view."""

    start_text = ft.Text("No accounts connected yet")
    input_panel = ft.Container()
    email_input = ft.TextField(label="Email Address", hint_text="Enter your email", width=300)
    password_input = ft.TextField(
        label="Password",
        hint_text="Enter your password",
        password=True,
        can_reveal_password=True,
        width=300,
    )
    host_input = ft.TextField(label="Host", hint_text="Enter your host name", width=300)
    # Liste mit emails um überprüfen
    connected_emails = []
    email_controllers = {}

    def add_account_click(e):
        # Hier muss man email addieren
        input_panel.content = ft.Column(
            [
                ft.Text("Add Email Account", size=16, weight=ft.FontWeight.BOLD),
                email_input,
                password_input,
                host_input,
                ft.Row(
                    [
                        ft.OutlinedButton("Connect", icon=ft.Icons.CHECK, on_click=connect_account),
                        ft.OutlinedButton("Cancel", icon=ft.Icons.CLOSE, on_click=cancel_add),
                    ],
                    spacing=10,
                ),
            ],
            spacing=10,
        )

        # Versteckt die "Add Email Account" Button
        add_button.visible = False

        page.update()

    def connect_account(e):
        # ob name und passport getippt sind
        if not email_input.value or not password_input.value or not host_input.value:
            show_snackbar("Please fill in all fields", ft.Colors.RED_400)
            return

        # ob email schon angemedet ist
        if email_input.value in connected_emails:
            show_snackbar("This email account is already connected", ft.Colors.ORANGE_400)
            return

        try:
            show_snackbar("Connecting...", ft.Colors.BLUE_400)

            print(f"Trying to connect: {email_input.value}@{host_input.value}")
            controller = EmailController(
                username=email_input.value, password=password_input.value, host=host_input.value
            )

            result = controller.login()
            print(f"Result: {result}")
            if result["status"] == "success":
                email_controllers[email_input.value] = controller
                connected_emails.append(email_input.value)
                start_text.visible = False

                show_snackbar("Connected!", ft.Colors.GREEN_400)
            else:
                show_snackbar(f"Failed: {result['message']}", ft.Colors.RED_400)
                page.update()
                return
        except Exception as ex:
            show_snackbar(f"Error: {str(ex)}", ft.Colors.RED_400)
            page.update()
            return

        new_account = ft.Container(
            ft.Row(
                [
                    ft.Icon(ft.Icons.EMAIL, color=ft.Colors.BLUE),
                    ft.Text(email_input.value, expand=True),
                    ft.IconButton(
                        icon=ft.Icons.DELETE,
                        icon_color=ft.Colors.RED,
                        tooltip="Remove account",
                        on_click=remove_account(email_input.value),
                    ),
                ]
            ),
            border=ft.border.all(1, ft.Colors.GREY_400),
            border_radius=5,
            padding=10,
        )

        # Fügt den neuen Account vor dem input_panel ein
        create_connected_email_accounts.content.controls.insert(-2, new_account)

        # Leert die Eingabefelder
        email_input.value = ""
        password_input.value = ""
        host_input.value = ""

        input_panel.content = None

        add_button.visible = True
        page.update()

    def remove_account(email_to_remove):
        def handler(e):
            # entfernt email aus dem List
            if email_to_remove in email_controllers:
                email_controllers[email_to_remove].logout()
                del email_controllers[email_to_remove]
            connected_emails.remove(email_to_remove)
            # entfernt der container mit account
            create_connected_email_accounts.content.controls.remove(e.control.parent.parent)

            # Zeigt "No accounts connected yet", falls keine Accounts da
            if len(connected_emails) == 0:
                start_text.visible = True

                page.update()

        return handler

    def cancel_add(e):
        email_input.value = ""
        password_input.value = ""
        host_input.value = ""

        input_panel.content = None
        add_button.visible = True
        page.update()

    def show_snackbar(message, color):
        snack_bar = ft.SnackBar(ft.Text(message), bgcolor=color)
        page.overlay.append(snack_bar)
        snack_bar.open = True
        page.update()

    add_button = ft.Container(
        ft.OutlinedButton(
            "Add Email Account",
            icon=ft.Icons.ADD,
            on_click=add_account_click,
        ),
        alignment=ft.alignment.center,
        margin=ft.margin.only(top=20),
    )

    create_connected_email_accounts = ft.Container(
        ft.Column(
            [
                ft.Text("Email Accounts", size=18, weight=ft.FontWeight.BOLD),
                ft.Text("Manage your email accounts"),
                ft.Divider(height=2, color=ft.Colors.GREY_400),
                start_text,
                add_button,
                input_panel,
            ],
            spacing=15,
        ),
        padding=20,
        border_radius=10,
        alignment=ft.alignment.center_left,
    )

    return create_connected_email_accounts
