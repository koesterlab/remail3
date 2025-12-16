import flet as ft

from remail.client.state.app_state import AppState
from remail.controllers.email_controller import EmailController
from remail.interfaces.email.services.user_service import UserService


def create_email_accounts_view(page: ft.Page, app_state: AppState) -> ft.Container:
    """Create the email accounts settings view."""

    # Bestehende Konten aus der Datenbank laden
    saved_users = UserService.get_all_users()
    print(f" Loaded {len(saved_users)} saved accounts from database")

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

    # Listen mit gespeicherten Daten initialisieren
    connected_emails = [user.email for user in saved_users]
    email_controllers = {}

    # "No accounts" ausblenden, falls gespeicherte Konten vorhanden sind
    if saved_users:
        start_text.visible = False

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
        # Überprüfen, ob alle Felder ausgefüllt sind
        if not email_input.value or not password_input.value or not host_input.value:
            show_snackbar("Please fill in all fields", ft.Colors.RED_400)
            return

        # Überprüfen, ob Email bereits hinzugefügt wurde
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
                # In der Datenbank speichern
                try:
                    new_user = UserService.add_user(
                        email=email_input.value,
                        password=password_input.value,
                        # Name wird automatisch aus der Email generiert
                        # Protokoll ist standardmäßig IMAP
                    )

                    print(f" User saved to database: {new_user.email} (ID: {new_user.id})")
                    show_snackbar("Connected and saved!", ft.Colors.GREEN_400)

                except ValueError as ve:
                    # Email existiert bereits in der Datenbank
                    print(f" Database warning: {ve}")
                    show_snackbar("Connected! (already in database)", ft.Colors.GREEN_400)

                except Exception as db_error:
                    print(f" Database error: {db_error}")
                    show_snackbar(f"Connected but save failed: {db_error}", ft.Colors.ORANGE_400)

                # Controller speichern und zur Liste hinzufügen
                email_controllers[email_input.value] = controller
                connected_emails.append(email_input.value)
                start_text.visible = False

            else:
                show_snackbar(f"Failed: {result['message']}", ft.Colors.RED_400)
                page.update()
                return

        except Exception as ex:
            show_snackbar(f"Error: {str(ex)}", ft.Colors.RED_400)
            page.update()
            return

        # UI-Element für neues Konto erstellen
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

        # Zum UI hinzufügen
        create_connected_email_accounts.content.controls.insert(-2, new_account)

        # Eingabefelder leeren
        email_input.value = ""
        password_input.value = ""
        host_input.value = ""

        input_panel.content = None
        add_button.visible = True
        page.update()

    def remove_account(email_to_remove):
        def handler(e):
            # Aus der Datenbank löschen
            try:
                deleted = UserService.delete_user(email_to_remove)
                if deleted:
                    print(f" User deleted from database: {email_to_remove}")
                else:
                    print(f" User not found in database: {email_to_remove}")
            except Exception as db_error:
                print(f" Database delete error: {db_error}")

            # Logout und aus dem Speicher entfernen
            if email_to_remove in email_controllers:
                email_controllers[email_to_remove].logout()
                del email_controllers[email_to_remove]

            connected_emails.remove(email_to_remove)
            create_connected_email_accounts.content.controls.remove(e.control.parent.parent)

            # "No accounts" anzeigen, falls die Liste leer ist
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

    # Geladene Konten aus der Datenbank anzeigen
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
        # Vor add_button und input_panel einfügen
        create_connected_email_accounts.content.controls.insert(-2, account_container)

    return create_connected_email_accounts
