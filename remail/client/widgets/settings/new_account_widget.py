from collections.abc import Callable
from typing import Any

import flet as ft

from remail.client import show_snack_bar
from remail.controllers.account_controller import AccountController
from remail.controllers.dtos.user_dto import UserDTO
from remail.controllers.email_controller import EmailController
from remail.enums import AuthMethods, ConnectionSecurity, Protocol


def create_add_email_widget(on_created: Callable[[UserDTO], Any]) -> ft.Container:
    """
    Liefert ein Container-Widget, das eine UI für das Hinzufügen einer E-Mail-Adresse bereitstellt.

    WICHTIG: Vor dem Verwenden muss der Aufrufer eine Callback-Funktion registrieren:
        widget.on_password_verify = lambda data, password: bool

    Die Callback erhält (data: dict, password: str) und muss True/False zurückgeben.
    """
    # --- Felder (sichtbar / unsichtbar steuern wir später) ---
    name_tf = ft.TextField(label="Anzeigename", width=400)
    email_tf = ft.TextField(label="E-Mail-Adresse", width=400)
    password_tf = ft.TextField(password=True, label="Password", width=400)

    # IMAP Felder (advanced)
    imap_host_tf = ft.TextField(label="IMAP Host", width=380)
    imap_host_port_tf = ft.TextField(label="IMAP Port", width=30)
    imap_user_tf = ft.TextField(label="IMAP Username", width=220)
    imap_password_tf = ft.TextField(password=True, label="IMAP Password", width=400)
    imap_password_type_dd = ft.Dropdown(
        width=160,
        label="Password-Type",
        value=ConnectionSecurity.SSL_TLS.value,
        options=[
            ft.dropdown.Option(key=ConnectionSecurity.SSL_TLS.value, text="SSL_TLS"),
            ft.dropdown.Option(key=ConnectionSecurity.STARTTLS.value, text="STARTTLS"),
            ft.dropdown.Option(key=ConnectionSecurity.PLAIN.value, text="Plain (Not recommend)"),
        ],
    )

    # SMTP Felder (advanced)
    smtp_host_tf = ft.TextField(label="SMTP Host", width=380)
    smtp_host_port_tf = ft.TextField(label="SMTP Port", width=30)
    smtp_user_tf = ft.TextField(label="SMTP Username", width=220)
    smtp_password_tf = ft.TextField(password=True, label="IMAP Password", width=400)
    smtp_password_type_dd = ft.Dropdown(
        width=160,
        label="Password-Type",
        value=ConnectionSecurity.SSL_TLS.value,
        options=[
            ft.dropdown.Option(key=ConnectionSecurity.SSL_TLS.value, text="SSL_TLS"),
            ft.dropdown.Option(key=ConnectionSecurity.STARTTLS.value, text="STARTTLS"),
            ft.dropdown.Option(key=ConnectionSecurity.PLAIN.value, text="Plain (Not recommend)"),
        ],
    )

    # Advanced-Panel (anfangs ausgeblendet)
    advanced_container = ft.Column(
        [
            ft.Text("IMAP / Eingehend", weight=ft.FontWeight.BOLD),
            ft.Row(
                [
                    imap_host_tf,
                    imap_host_port_tf,
                    imap_user_tf,
                    imap_password_tf,
                    imap_password_type_dd,
                ],
                wrap=True,
            ),
            ft.Divider(),
            ft.Text("SMTP / Ausgehend", weight=ft.FontWeight.BOLD),
            ft.Row(
                [
                    smtp_host_tf,
                    smtp_host_port_tf,
                    smtp_user_tf,
                    smtp_password_tf,
                    smtp_password_type_dd,
                ],
                wrap=True,
            ),
        ],
        visible=False,
        tight=True,
    )

    advanced_toggle_icon = ft.Icon(icon=ft.Icons.ARROW_DROP_DOWN)

    container = ft.Container()

    def set_defaults_from_email(e=None):
        txt = email_tf.value or ""
        if "@" in txt:
            local, domain = txt.split("@", 1)
            # nur setzen wenn leere Felder (als Default)
            if not imap_user_tf.value:
                imap_user_tf.value = local
            if not smtp_user_tf.value:
                smtp_user_tf.value = local
            # Host-Defaults: nutze domain oder prefixed host
            if not imap_host_tf.value:
                imap_host_tf.value = f"imap.{domain}"
            if not smtp_host_tf.value:
                smtp_host_tf.value = f"smtp.{domain}"
        # password
        if not imap_password_tf.value:
            imap_password_tf.value = password_tf.value
        if not smtp_password_tf.value:
            smtp_password_tf.value = password_tf.value

        if e is not None:
            e.page.update()

    # binden: bei Änderung der Email Felder
    email_tf.on_change = set_defaults_from_email

    # --- Advanced ein/ausklappen ---
    def toggle_advanced(e: ft.Event[ft.Button]):
        advanced_container.visible = not advanced_container.visible
        advanced_toggle_icon.icon = (
            ft.Icons.ARROW_DROP_UP if advanced_container.visible else ft.Icons.ARROW_DROP_DOWN
        )
        # wenn advanced gerade aufgeklappt wurde, setze Defaults aus Email
        if advanced_container.visible:
            set_defaults_from_email()
        e.page.update()

    advanced_btn = ft.Button(
        content=ft.Row(
            [ft.Text("Advanced settings"), advanced_toggle_icon],
            alignment=ft.MainAxisAlignment.CENTER,
        ),
        elevation=2,
        on_click=toggle_advanced,
    )

    # --- Passwort Dialog & Prüf-Workflow ---
    def on_add_click():
        if not email_tf.value or "@" not in email_tf.value:
            show_snack_bar(ft.Text("Bitte zuerst eine gültige E-Mail-Adresse eingeben."))
            return
        username, host = email_tf.value.split("@")[:2]
        protocol = EmailController().check_credentials(
            imap_username=imap_user_tf.value or username,
            imap_host=imap_host_tf.value or host,
            imap_port=int(imap_host_port_tf.value or 993),
            imap_password=imap_password_tf.value or password_tf.value,
            imap_security=ConnectionSecurity[imap_password_type_dd.value or "ssl_tls"],
            imap_method=AuthMethods.PASSWORD,
            smtp_username=smtp_user_tf.value or username,
            smtp_host=smtp_host_tf.value or host,
            smtp_port=int(smtp_host_tf.value or 587),
            smtp_password=smtp_password_tf.value or password_tf.value,
            smtp_security=ConnectionSecurity[smtp_password_type_dd.value or "ssl_tls"],
            smtp_method=AuthMethods.PASSWORD,
        )

        if protocol:
            acc = AccountController.create_new_account(
                name_tf.value, email_tf.value, protocol, Protocol.IMAP
            )
            on_created(acc)
            ft.SnackBar(ft.Text("Account Connected"))
        else:
            ft.SnackBar(ft.Text("Connection failed"))

    add_btn = ft.Button(content=ft.Text("Hinzufügen"), on_click=on_add_click)

    # Layout zusammenbauen
    main_col = ft.Column(
        [
            ft.Row([name_tf]),
            ft.Row([email_tf, password_tf]),
            ft.Row([advanced_btn], alignment=ft.MainAxisAlignment.START),
            advanced_container,
            ft.Row([add_btn], alignment=ft.MainAxisAlignment.END),
        ],
        tight=True,
    )

    # Container füllen und zurückgeben
    container.content = main_col

    # Beschreibung/Contract: caller muss callback setzen: container.on_password_verify = callable
    container.tooltip = "Setze container.on_password_verify = lambda data,pw: bool"

    return container
