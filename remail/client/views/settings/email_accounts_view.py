import flet as ft

from remail.client.scheduler import Scheduler
from remail.client.state.app_state import AppState
from remail.controllers.email_controller import EmailController
from remail.interfaces.email.services.email_sync_service import EmailSyncService
from remail.interfaces.email.services.user_service import UserService


def create_email_accounts_view(page: ft.Page, app_state: AppState) -> ft.Container:
    """Create the email accounts settings view."""

    saved_users = UserService.get_all_users()

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

    app_state.connected_emails = [user.email for user in saved_users]

    if saved_users:
        start_text.visible = False

    def on_sync_complete(result: dict) -> None:
        """Callback when email sync completes."""

        synced = result.get("synced_count", 0)

        if synced > 0:
            show_snackbar(f"Synced {synced} new email(s)", ft.Colors.GREEN_400)

    def on_sync_error(error: str) -> None:
        """Callback when email sync fails."""

        # Don't show snackbar for background sync errors to avoid spam
        pass

    def add_account_click(e):
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
        add_button.visible = False

        page.update()

    def connect_account(e):
        if not email_input.value or not password_input.value or not host_input.value:
            show_snackbar("Please fill in all fields", ft.Colors.RED_400)

            return

        if email_input.value in app_state.connected_emails:
            show_snackbar("This email account is already connected", ft.Colors.ORANGE_400)

            return

        user_email = email_input.value

        try:
            show_snackbar("Connecting...", ft.Colors.BLUE_400)

            controller = EmailController(
                username=email_input.value, password=password_input.value, host=host_input.value
            )
            result = controller.login()

            if result["status"] == "success":
                try:
                    UserService.add_user(
                        email=email_input.value,
                        password=password_input.value,
                    )

                    show_snackbar("Connected and saved!", ft.Colors.GREEN_400)

                except ValueError:
                    show_snackbar("Connected! (already in database)", ft.Colors.GREEN_400)

                except Exception as db_error:
                    show_snackbar(f"Connected but save failed: {db_error}", ft.Colors.ORANGE_400)

                app_state.connected_emails.append(email_input.value)

                start_text.visible = False

                sync_service = EmailSyncService(
                    protocol=controller.protocol,
                    email_parser=controller.protocol.email_parser,
                    user_email=user_email,
                )
                scheduler = Scheduler(
                    task=sync_service.sync_emails,
                    sync_interval=60,  # Sync every 60 seconds
                    on_complete=on_sync_complete,
                    on_error=on_sync_error,
                )
                app_state.add_email_scheduler(user_email, scheduler)
                scheduler.start()

                show_snackbar("Connected! Syncing emails...", ft.Colors.GREEN_400)
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
                    ft.Text(user_email, expand=True),
                    ft.IconButton(
                        icon=ft.Icons.DELETE,
                        icon_color=ft.Colors.RED,
                        tooltip="Remove account",
                        on_click=remove_account(user_email),
                    ),
                ]
            ),
            border=ft.border.all(1, ft.Colors.GREY_400),
            border_radius=5,
            padding=10,
        )

        create_connected_email_accounts.content.controls.insert(-2, new_account)

        email_input.value = ""
        password_input.value = ""
        host_input.value = ""

        input_panel.content = None
        add_button.visible = True

        page.update()

    def remove_account(email_to_remove):
        def handler(e):
            try:
                UserService.delete_user(email_to_remove)
            except Exception as e:
                show_snackbar(f"Failed to remove user: {e}", ft.Colors.ORANGE_400)

            app_state.remove_email_scheduler(email_to_remove)
            app_state.connected_emails.remove(email_to_remove)
            create_connected_email_accounts.content.controls.remove(e.control.parent.parent)

            if len(app_state.connected_emails) == 0:
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

    for user in saved_users:
        account_container = ft.Container(
            ft.Row(
                [
                    ft.Icon(ft.Icons.EMAIL, color=ft.Colors.BLUE),
                    ft.Text(user.email, expand=True),
                    ft.IconButton(
                        icon=ft.Icons.DELETE,
                        icon_color=ft.Colors.RED,
                        tooltip="Remove account",
                        on_click=remove_account(user.email),
                    ),
                ]
            ),
            border=ft.border.all(1, ft.Colors.GREY_400),
            border_radius=5,
            padding=10,
        )
        create_connected_email_accounts.content.controls.insert(-2, account_container)

    return create_connected_email_accounts
