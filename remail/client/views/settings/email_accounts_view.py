import flet as ft

from remail.client.state import MainAppState, MainAppStateProperties
from remail.client.views.settings.settings_sub_view import SettingsSubView
from remail.controllers.account_controller import AccountController
from remail.controllers.dtos import SettingsDTO
from remail.controllers.dtos.user_dto import UserDTO
from remail.controllers.email_controller import EmailController
from remail.enums import AuthMethods, ConnectionSecurity, Protocol
from remail.interfaces.email.protocols.exchange import ExchangeProtocol


class EmailAccountsView(SettingsSubView):
    def __init__(self, state: MainAppState | None = None):
        self._app_state = state
        super().__init__()

    def create_page(self, settings: SettingsDTO) -> ft.Container:
        """Create the email accounts settings view."""

        smtp_user_input = ft.TextField(label="Username", hint_text="Enter SMTP username")
        smtp_pass_input = ft.TextField(
            label="Password",
            hint_text="Enter SMTP password",
            password=True,
            can_reveal_password=True,
        )
        smtp_port_input = ft.TextField(label="Port", hint_text="587")
        imap_user_input = ft.TextField(label="Username", hint_text="Enter IMAP username")
        imap_pass_input = ft.TextField(
            label="Password",
            hint_text="Enter IMAP password",
            password=True,
            can_reveal_password=True,
        )
        imap_port_input = ft.TextField(label="Port", hint_text="993")

        # ---------------- Snackbar ----------------
        def show_snackbar(message, color):
            snack_bar = ft.SnackBar(ft.Text(message), bgcolor=color)
            self.page.overlay.append(snack_bar)
            snack_bar.open = True
            self.page.update()

        # ---------------- Dialog Helper ----------------
        def close_dialog(dlg):
            dlg.open = False
            self.page.update()

        # ---------------- Advanced SMTP/IMAP Dialogs ----------------
        def on_smtp_settings(e):
            dlg = ft.AlertDialog(
                title=ft.Text("Advanced SMTP Settings"),
                content=ft.Column(
                    [smtp_user_input, smtp_pass_input, smtp_port_input],
                    scroll=ft.ScrollMode.AUTO,
                    spacing=10,
                ),
                actions=[
                    ft.TextButton("Cancel", on_click=lambda e: close_dialog(dlg)),
                    ft.TextButton(
                        "Save",
                        on_click=lambda e: (
                            show_snackbar("SMTP settings saved!", ft.Colors.GREEN_400),
                            close_dialog(dlg),
                        ),
                    ),
                ],
            )
            self.page.overlay.append(dlg)
            dlg.open = True
            self.page.update()

        def on_imap_settings(e):
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
            self.page.overlay.append(dlg)
            dlg.open = True
            self.page.update()

        # ---------------- UI Inputs ----------------
        name_input = ft.TextField(label="Display Name", hint_text="Your Name", width=300)
        email_input = ft.TextField(
            label="Email address", hint_text="Enter your email address", width=300
        )
        password_input = ft.TextField(
            label="Password",
            hint_text="Enter your password",
            password=True,
            can_reveal_password=True,
            width=300,
        )
        imap_host_input = ft.TextField(
            label="IMAP Host",
            hint_text="Enter your IMAP host name",
            width=300,
            suffix=ft.IconButton(
                icon=ft.Icons.SETTINGS, tooltip="Settings", on_click=on_imap_settings
            ),
        )
        smtp_host_input = ft.TextField(
            label="SMTP Host",
            hint_text="Enter your SMTP host name",
            width=300,
            suffix=ft.IconButton(
                icon=ft.Icons.SETTINGS, tooltip="Settings", on_click=on_smtp_settings
            ),
        )
        exchange_input = ft.TextField(
            label="Exchange Server", hint_text="Enter your Exchange server name", width=300
        )

        input_panel = ft.Container()

        # ---------------- Add Account ----------------
        def add_account_click(e):
            tabs = ft.Tabs(
                length=2,
                content=ft.Column(
                    controls=[
                        ft.TabBar(
                            tabs=[
                                ft.Tab(label="IMAP"),
                                ft.Tab(label="Exchange"),
                            ]
                        ),
                        ft.TabBarView(
                            height=350,
                            controls=[
                                ft.Column(
                                    [
                                        name_input,
                                        email_input,
                                        password_input,
                                        imap_host_input,
                                        smtp_host_input,
                                    ],
                                    spacing=10,
                                ),
                                ft.Column(
                                    [
                                        name_input,
                                        email_input,
                                        password_input,
                                        exchange_input,
                                    ],
                                    spacing=10,
                                ),
                            ],
                        ),
                    ],
                ),
            )

            input_panel.content = ft.Column(
                [
                    ft.Text("Add Email Account", size=16, weight=ft.FontWeight.BOLD),
                    tabs,
                    ft.Row(
                        [
                            ft.OutlinedButton(
                                "Connect",
                                icon=ft.Icons.CHECK,
                                on_click=lambda e: connect_account(e, tabs),
                            ),
                            ft.OutlinedButton("Cancel", icon=ft.Icons.CLOSE, on_click=cancel_add),
                        ],
                        spacing=10,
                    ),
                ],
                spacing=10,
                scroll=ft.ScrollMode.AUTO,
            )
            add_button.visible = False
            self.page.update()

        # ---------------- Connect Account ----------------

        def connect_account(e, tabs=None):
            selected = tabs.selected_index if tabs else 0

            if selected == 0:  # IMAP
                if (
                    not email_input.value
                    or not password_input.value
                    or not imap_host_input.value
                    or not smtp_host_input.value
                ):
                    show_snackbar("Please fill in all fields", ft.Colors.RED_400)
                    return
                try:
                    show_snackbar("Connecting...", ft.Colors.BLUE_400)
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
                        AccountController.create_new_account(
                            name_input.value.strip(),
                            email_input.value.strip().lower(),
                            conn,
                            Protocol.IMAP,
                        )
                        if self._app_state is not None:
                            self._app_state.set(
                                MainAppStateProperties.ACCOUNTS_CHANGED,
                                email_input.value.strip().lower(),
                            )
                        show_snackbar("Account added", ft.Colors.PRIMARY_CONTAINER)
                    else:
                        show_snackbar("Connection failed", ft.Colors.ERROR)
                    cancel_add(None)
                    update_account_view()
                except Exception as ex:
                    show_snackbar(f"Error: {str(ex)}", ft.Colors.RED_400)

            else:  # Exchange
                if (
                    not name_input.value
                    or not email_input.value
                    or not password_input.value
                    or not exchange_input.value
                ):
                    show_snackbar("Please fill in all fields", ft.Colors.RED_400)
                    return
                try:
                    show_snackbar("Connecting...", ft.Colors.BLUE_400)
                    protocol = ExchangeProtocol(
                        username=email_input.value.strip().lower(),
                        password=password_input.value,
                        server=exchange_input.value.strip(),
                    )
                    if protocol.test_connection():
                        AccountController.create_new_account(
                            name_input.value.strip(),
                            email_input.value.strip().lower(),
                            protocol,
                            Protocol.EXCHANGE,
                        )
                        if self._app_state is not None:
                            self._app_state.set(
                                MainAppStateProperties.ACCOUNTS_CHANGED,
                                email_input.value.strip().lower(),
                            )
                        show_snackbar("Account added", ft.Colors.PRIMARY_CONTAINER)
                    else:
                        show_snackbar("Connection failed", ft.Colors.ERROR)
                    cancel_add(None)
                    update_account_view()
                except Exception as ex:
                    show_snackbar(f"Error: {str(ex)}", ft.Colors.RED_400)

        # ---------------- Remove Account ----------------
        def remove_account(user: UserDTO):
            def handler(e):
                try:
                    AccountController(user.id).delete()
                    if self._app_state is not None:
                        self._app_state.set(MainAppStateProperties.ACCOUNTS_CHANGED, user.email)
                except Exception as ex:
                    show_snackbar(f"Failed to remove user: {ex}", ft.Colors.ORANGE_400)

                # Remove UI element
                update_account_view()

            return handler

        # ---------------- Edite Account ----------------
        def edit_account(user):
            controller = AccountController(user.id)
            connection = controller.get_connection_data()

            imap_username = connection.get("imap_username", "")
            smtp_username = connection.get("smtp_username", "")
            edit_name_input = ft.TextField(
                label="Display Name",
                value=user.name,
            )

            edit_password_input = ft.TextField(
                label="Password",
                value=connection.get("imap_password", ""),
                password=True,
                can_reveal_password=True,
            )
            edit_imap_host_input = ft.TextField(
                label="Host",
                value=connection.get("imap_host", ""),
            )

            edit_imap_port_input = ft.TextField(
                label="Port",
                value=str(connection.get("imap_port", 993)),
            )

            edit_smtp_host_input = ft.TextField(
                label="Host",
                value=connection.get("smtp_host", ""),
            )

            edit_smtp_port_input = ft.TextField(
                label="Port",
                value=str(connection.get("smtp_port", 587)),
            )

            def update_account(e,dlg):
                edit_imap_host_input.border_color = None
                edit_imap_port_input.border_color = None

                edit_smtp_host_input.border_color = None
                edit_smtp_port_input.border_color = None
                edit_password_input.border_color = None
                connection_changed = (
                        edit_password_input.value != connection.get("imap_password", "")
                        or edit_imap_host_input.value != connection.get("imap_host", "")
                        or edit_imap_port_input.value != str(connection.get("imap_port", 993))
                        or edit_smtp_host_input.value != connection.get("smtp_host", "")
                        or edit_smtp_port_input.value != str(connection.get("smtp_port", 587))
                )

                if connection_changed:

                    result = EmailController().check_credentials(
                        imap_username=imap_username,
                        imap_password=edit_password_input.value,
                        imap_host=edit_imap_host_input.value,
                        imap_port=int(edit_imap_port_input.value),
                        imap_security=ConnectionSecurity.SSL_TLS,
                        imap_method=AuthMethods.PASSWORD,

                        smtp_username=smtp_username,
                        smtp_password=edit_password_input.value,
                        smtp_host=edit_smtp_host_input.value,
                        smtp_port=int(edit_smtp_port_input.value),
                        smtp_security=ConnectionSecurity.SSL_TLS,
                        smtp_method=AuthMethods.PASSWORD,
                    )

                    if not result["imap_ok"]:
                        edit_imap_host_input.border_color = ft.Colors.RED
                        edit_imap_port_input.border_color = ft.Colors.RED

                    if not result["smtp_ok"]:
                        edit_smtp_host_input.border_color = ft.Colors.RED
                        edit_smtp_port_input.border_color = ft.Colors.RED

                    if not result["imap_ok"] and not result["smtp_ok"]:
                        edit_password_input.border_color = ft.Colors.RED
                    if not result["imap_ok"] or not result["smtp_ok"]:
                        self.page.update()
                        show_snackbar("Connection failed", ft.Colors.ERROR)
                        return

                controller.update_account(
                    edit_name_input.value.strip(),
                    edit_password_input.value,
                    edit_imap_host_input.value,
                    int(edit_imap_port_input.value),
                    edit_smtp_host_input.value,
                    int(edit_smtp_port_input.value),
                )

                show_snackbar(
                    "Account updated",
                    ft.Colors.GREEN_400,
                )

                close_dialog(dlg)


                cancel_add(None)
                self._app_state.set(MainAppStateProperties.ACCOUNTS_CHANGED, user.email)
                self._app_state.trigger(MainAppStateProperties.ACCOUNTS_CHANGED)
                update_account_view()





            dlg = ft.AlertDialog(
                    title=ft.Text("Edit Email Account"),
                    content=ft.Column(
                        [
                            ft.Text(
                                user.email,
                                size=14,
                                color=ft.Colors.GREY_500,
                            ),

                            ft.Divider(),

                            ft.Text(
                                "Account Information",
                                weight=ft.FontWeight.BOLD,
                            ),

                            ft.Row([
                                edit_name_input,
                                edit_password_input,
                            ]),

                            ft.Divider(),

                            ft.Text(
                                "IMAP Settings",
                                weight=ft.FontWeight.BOLD,
                            ),

                            ft.Row([
                                edit_imap_host_input,
                                edit_imap_port_input,
                            ]),

                            ft.Divider(),

                            ft.Text(
                                "SMTP Settings",
                                weight=ft.FontWeight.BOLD,
                            ),

                            ft.Row([
                                edit_smtp_host_input,
                                edit_smtp_port_input,
                            ]),
                        ],
                        spacing=10,
                        tight=True,
                    ),
                    actions=[
                        ft.TextButton(
                            "Cancel",
                            on_click=lambda e: close_dialog(dlg),
                        ),
                        ft.FilledButton(
                            "Update",
                            on_click=lambda e: (
                                update_account(e, dlg),

                            ),
                        ),
                    ],
                )
            self.page.overlay.append(dlg)
            dlg.open = True
            self.page.update()
            update_account_view()


        # ---------------- Cancel Add ----------------
        def cancel_add(e):
            email_input.value = ""
            password_input.value = ""
            imap_host_input.value = ""
            smtp_host_input.value = ""
            exchange_input.value = ""
            input_panel.content = None
            add_button.visible = True
            self.page.update()

        # ---------------- UI Containers ----------------
        add_button = ft.Container(
            ft.OutlinedButton("Add Email Account", icon=ft.Icons.ADD, on_click=add_account_click),
            alignment=ft.Alignment.CENTER,
            margin=ft.Margin.only(top=20),
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
                        ft.Text(f"{c if c > 0 else 'No'} accounts connected", size=12),
                        ft.Column(
                            [
                                ft.Text("No accounts connected", size=12)
                                if not accounts
                                else ft.Container(
                                    ft.Row(
                                        [
                                            ft.Icon(ft.Icons.EMAIL, color=ft.Colors.BLUE),
                                            ft.Text(user.name, expand=True),
                                            ft.IconButton(
                                                icon=ft.Icons.EDIT,
                                                tooltip="Edit account",
                                                on_click=lambda e,  c=user: edit_account(c),
                                            ),
                                            ft.IconButton(
                                                icon=ft.Icons.DELETE,
                                                icon_color=ft.Colors.RED,
                                                tooltip="Remove account",
                                                on_click=remove_account(user),
                                            ),
                                        ]
                                    ),
                                    border=ft.Border.all(1, ft.Colors.GREY_400),
                                    border_radius=5,
                                    padding=10,
                                )
                                for user in [acc.get_user() for acc in accounts]
                            ]
                        ),
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
            except RuntimeError as _:
                pass

        update_account_view()
        return base
