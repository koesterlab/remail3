import datetime

import flet as ft

from remail.client.state import MainAppState, MainAppStateProperties
from remail.controllers.dtos.conversations import ConversationDTO, ThreadPreviewDTO


def open_compose_dialog(state: MainAppState, page: ft.Page | None) -> None:
    if not page:
        return

    error_text = ft.Text("", color=ft.Colors.ERROR, size=12, visible=False)

    to_field = ft.TextField(
        hint_text="To (e.g. name@example.com)",
        border_radius=8,
        dense=True,
        autofocus=True,
    )
    subject_field = ft.TextField(
        hint_text="Subject",
        border_radius=8,
        dense=True,
    )

    def close():
        dialog.open = False
        page.update()

    def on_cancel(_):
        close()

    def on_compose(_):
        email = to_field.value.strip()
        subject = subject_field.value.strip() or "(no subject)"

        if not email or "@" not in email:
            error_text.value = "Please enter a valid email address."
            error_text.visible = True
            error_text.update()
            return

        try:
            contact = state.get_active_email_account().find_or_create_contact_by_email(email)
        except Exception:
            error_text.value = "Could not find or create contact."
            error_text.visible = True
            error_text.update()
            return

        thread = ThreadPreviewDTO(-1, subject, 0, 0, "", datetime.datetime.now())
        conversation = ConversationDTO(-1, [contact], [thread], False, None)

        close()
        state.set(MainAppStateProperties.ACTIVE_THREAD_CONVERSATION, conversation)
        state.set(MainAppStateProperties.ACTIVE_THREAD, thread)

    dialog = ft.AlertDialog(
        title=ft.Text("New Message"),
        content=ft.Column(
            [to_field, subject_field, error_text],
            tight=True,
            spacing=10,
            width=400,
        ),
        actions=[
            ft.TextButton("Cancel", on_click=on_cancel),
            ft.TextButton("Compose", on_click=on_compose),
        ],
        actions_alignment=ft.MainAxisAlignment.END,
    )

    page.overlay.append(dialog)
    dialog.open = True
    page.update()
