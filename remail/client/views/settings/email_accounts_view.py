import flet as ft

from remail.client.state.app_state import AppState
from remail.controllers.account_controller import AccountController
from remail.controllers.dtos.user_dto import UserDTO
from remail.controllers.email_controller import EmailController
from remail.enums import ConnectionSecurity, AuthMethods, Protocol


def create_email_accounts_view(page: ft.Page, app_state: AppState) -> ft.Container:
    """Create the email accounts settings view."""

    smtp_user_input = ft.TextField(label="Username", hint_text="Enter SMTP username")
    smtp_pass_input = ft.TextField(label="Password", hint_text="Enter SMTP password", password=True,
                                    can_reveal_password=True)
    smtp_port_input = ft.TextField(label="Port", hint_text="587")
    imap_user_input = ft.TextField(label="Username", hint_text="Enter IMAP username")
    imap_pass_input = ft.TextField(label="Password", hint_text="Enter IMAP password", password=True,
                                    can_reveal_password=True)
    imap_port_input = ft.TextField(label="Port", hint_text="993")

    # ---------------- Snackbar ----------------
    def show_snackbar(message, color):
        snack_bar = ft.SnackBar(ft.Text(message), bgcolor=color)
        page.overlay.append(snack_bar)
        snack_bar.open = True
        page.update()

    # ---------------- Dialog Helper ----------------
    def close_dialog(dlg):
        dlg.open = False
        page.update()

    # ---------------- Advanced SMTP/IMAP Dialogs ----------------
    def on_smtp_settings():
        dlg = ft.AlertDialog(
            title=ft.Text("Advanced SMTP Settings"),
            content=ft.Column(
                [smtp_user_input, smtp_pass_input, smtp_port_input],
                scroll=ft.ScrollMode.AUTO,
                spacing=10,
            ),
            actions=[
                ft.TextButton("Cancel", on_click=lambda _: close_dialog(dlg)),
                ft.TextButton(
                    "Save",
                    on_click=lambda _: (
                        show_snackbar("SMTP settings saved!", ft.Colors.GREEN_400),
                        close_dialog(dlg),
                    ),
                ),
            ],
        )
        page.overlay.append(dlg)
        dlg.open = True
        page.update()

    def on_imap_settings():
        dlg = ft.AlertDialog(
            title=ft.Text("Advanced IMAP Settings"),
            content=ft.Column(
                [imap_user_input, imap_pass_input, imap_port_input],
                scroll=ft.ScrollMode.AUTO,
                spacing=10,
            ),
            actions=[
                ft.TextButton("Cancel", on_click=lambda e: close_dialog(dlg)),
                ft.TextButton(
                    "Save",
                    on_click=lambda e: (
                        show_snackbar("IMAP settings saved!", ft.Colors.GREEN_400),
                        close_dialog(dlg),
                    ),
                ),
            ],
        )
        page.overlay.append(dlg)
        dlg.open = True
        page.update()

    # ---------------- UI Inputs ----------------
    start_text = ft.Text("No accounts connected yet")

    name_input = ft.TextField(label="Display Name", hint_text="Your Name", width=300)
    email_input = ft.TextField(label="Email address", hint_text="Enter your email address", width=300)
    password_input = ft.TextField(label="Password", hint_text="Enter your password", password=True, can_reveal_password=True, width=300)
    imap_host_input = ft.TextField(
        label="IMAP Host",
        hint_text="Enter your IMAP host name",
        width=300,
        suffix=ft.IconButton(icon=ft.Icons.SETTINGS, tooltip="Settings", on_click=on_imap_settings),
    )
    smtp_host_input = ft.TextField(
        label="SMTP Host",
        hint_text="Enter your SMTP host name",
        width=300,
        suffix=ft.IconButton(icon=ft.Icons.SETTINGS, tooltip="Settings", on_click=on_smtp_settings),
    )

    input_panel = ft.Container()
    if app_state.connected_emails:
        start_text.visible = False

    # ---------------- Add Account ----------------
    def add_account_click():
        input_panel.content = ft.Column(
            [
                ft.Text("Add Email Account", size=16, weight=ft.FontWeight.BOLD),
                name_input,
                email_input,
                password_input,
                imap_host_input,
                smtp_host_input,
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

    # ---------------- Connect Account ----------------
    def connect_account():
        if not email_input.value or not password_input.value or not imap_host_input.value or not smtp_host_input.value:
            show_snackbar("Please fill in all fields", ft.Colors.RED_400)
            return

        try:
            show_snackbar("Connecting...", ft.Colors.BLUE_400)

            # --- Check credentials using EmailController ---
            if "@" not in email_input.value:
                show_snackbar("Email must contain '@'", ft.Colors.ERROR)
                return
            user, host = email_input.value.split("@")[:2]
            conn = EmailController().check_credentials(
                imap_username=imap_user_input.value or user,
                imap_password=imap_pass_input.value or password_input.value,
                imap_host=imap_host_input.value or host,
                imap_port=int(imap_port_input.value or 993),
                imap_security=ConnectionSecurity.SSL_TLS,
                imap_method=AuthMethods.PASSWORD,
                smtp_username=smtp_user_input.value or user,
                smtp_password=smtp_pass_input.value or password_input.value,
                smtp_host=smtp_host_input.value or host,
                smtp_port=int(smtp_port_input.value or 587),
                smtp_method=AuthMethods.PASSWORD,
                smtp_security=ConnectionSecurity.SSL_TLS,
            )

            if conn:
                AccountController.create_new_account(name_input.value.strip(), email_input.value.strip().lower(), conn, Protocol.IMAP)
                show_snackbar("Account added", ft.Colors.PRIMARY_CONTAINER)
            else:
                show_snackbar("Connection failed", ft.Colors.ERROR)

            cancel_add()  # reset input fields
            update_account_view()

        except Exception as ex:
            show_snackbar(f"Error: {str(ex)}", ft.Colors.RED_400)

    # ---------------- Remove Account ----------------
    def remove_account(user: UserDTO):
        def handler():
            try:
                AccountController(user.id).delete()
            except Exception as ex:
                show_snackbar(f"Failed to remove user: {ex}", ft.Colors.ORANGE_400)

            # Remove UI element
            update_account_view()
        return handler

    # ---------------- Cancel Add ----------------
    def cancel_add():
        email_input.value = ""
        password_input.value = ""
        imap_host_input.value = ""
        smtp_host_input.value = ""
        input_panel.content = None
        add_button.visible = True
        page.update()

    # ---------------- UI Containers ----------------
    add_button = ft.Container(
        ft.OutlinedButton("Add Email Account", icon=ft.Icons.ADD, on_click=add_account_click),
        alignment=ft.Alignment.CENTER,
        margin=ft.margin.only(top=20),
    )

    base = ft.Container()
    def update_account_view():
        accounts = AccountController.all_client_accounts()
        c = len(accounts)
        accounts_list = ft.Container(
            ft.Column(
                [
                    ft.Text("Email Accounts", size=18, weight=ft.FontWeight.BOLD),
                    ft.Text("Manage your email accounts"),
                    ft.Divider(height=2, color=ft.Colors.GREY_400),
                    ft.Text(f"{c if c > 0 else "No"} accounts connected", size=12),
                    ft.Column([
                        ft.Container(
                            ft.Row(
                                [
                                    ft.Icon(ft.Icons.EMAIL, color=ft.Colors.BLUE),
                                    ft.Text(user.name, expand=True),
                                    ft.IconButton(icon=ft.Icons.DELETE, icon_color=ft.Colors.RED,
                                                  tooltip="Remove account", on_click=remove_account(user)),
                                ]
                            ),
                            border=ft.border.all(1, ft.Colors.GREY_400),
                            border_radius=5,
                            padding=10,
                        ) for user in [acc.get_user() for acc in accounts]
                    ]),
                    add_button,
                    input_panel,
                ],
                spacing=15,
                scroll=ft.ScrollMode.AUTO,
            ),
            padding=20,
            border_radius=10,
            alignment=ft.Alignment.CENTER_LEFT,
            expand=True,
        )
        base.content = accounts_list
        try:
            base.update()
        except RuntimeError:
            pass

    update_account_view()
    return base
