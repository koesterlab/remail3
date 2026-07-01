import flet as ft

from remail import errors as ee
from remail.client.state import MainAppState, MainAppStateProperties


def create_new_message_dialog(state: MainAppState) -> ft.Container:
    expanded = False

    active_thread = state.get(MainAppStateProperties.ACTIVE_THREAD)
    needs_subject = active_thread and active_thread.thread_id < 0 and not active_thread.title

    def expand() -> None:
        nonlocal expanded
        expanded = True
        input_field.max_lines = 10
        input_field.min_lines = 10
        input_field.dense = False
        input_field.update()
        button_bar.visible = True
        button_bar.update()
        send_btn_bottom.visible = False
        send_btn_bottom.update()

    def collapse() -> None:
        nonlocal expanded
        expanded = False
        input_field.max_lines = 1
        input_field.min_lines = 1
        input_field.dense = True
        input_field.update()
        button_bar.visible = False
        button_bar.update()
        send_btn_bottom.visible = True
        send_btn_bottom.update()

    def on_blur() -> None:
        state.set(MainAppStateProperties.DRAFT, input_field.value)
        if input_field.value == "":
            collapse()

    subject_field = ft.TextField(
        hint_text="Subject...",
        visible=bool(needs_subject),
        border_radius=20,
        filled=True,
        bgcolor=ft.Colors.INVERSE_SURFACE,
        color=ft.Colors.ON_INVERSE_SURFACE,
        focused_border_color=ft.Colors.TRANSPARENT,
        border_color=ft.Colors.TRANSPARENT,
        dense=True,
        content_padding=ft.Padding.symmetric(vertical=6, horizontal=12),
    )

    input_field = ft.TextField(
        hint_text="Send a message...",
        border_radius=20,
        min_lines=1,
        max_lines=1,
        filled=True,
        bgcolor=ft.Colors.INVERSE_SURFACE,
        expand=True,
        color=ft.Colors.ON_INVERSE_SURFACE,
        on_focus=lambda _: expand(),
        on_blur=lambda e: on_blur(),
        on_change=lambda _: on_change(),
        multiline=True,
        focused_border_color=ft.Colors.TRANSPARENT,
        border_color=ft.Colors.TRANSPARENT,
    )

    def on_change() -> None:
        s = input_field.value
        send_btn_top.disabled = s == ""
        send_btn_bottom.disabled = s == ""
        send_btn_top.update()
        send_btn_bottom.update()

    def on_draft_change(s):
        input_field.value = s
        if not expanded:
            expand()
        on_change()

    def send_mail():
        thread = state.get(MainAppStateProperties.ACTIVE_THREAD)
        conversation = state.get(MainAppStateProperties.ACTIVE_THREAD_CONVERSATION)
        subject = thread.title or subject_field.value
        if not subject:
            return
        message = input_field.value

        if conversation.id < 0:  # creating new conversation
            conversation = state.get_active_email_account().create_conversation(
                conversation.contacts
            )
            created = state.thread_controller.create_thread(conversation.id, subject)
            thread_id = created.id
        elif thread.thread_id < 0:
            created = state.thread_controller.create_thread(conversation.id, subject)
            thread_id = created.id
        else:
            thread_id = thread.thread_id

        try:
            state.thread_controller.send_message(thread_id, message, [])
        except ee.EmailError:
            from remail.client import show_snack_bar
            show_snack_bar(ft.Text("Failed to send message. Please check your connection and try again."))
            return

        # clear
        state.set(MainAppStateProperties.DRAFT, "")
        input_field.value = ""
        input_field.update()

    state.register_observer(MainAppStateProperties.DRAFT, on_draft_change)
    send_btn_bottom = ft.IconButton(
        ft.Icons.SEND,
        on_click=lambda _: send_mail(),
        icon_color=ft.Colors.ON_INVERSE_SURFACE,
        disabled=True,
    )
    send_btn_top = ft.IconButton(
        ft.Icons.SEND,
        on_click=lambda _: send_mail(),
        icon_color=ft.Colors.ON_INVERSE_SURFACE,
        disabled=True,
    )

    button_bar = ft.Row(
        [
            ft.IconButton(
                ft.Icons.ARROW_DOWNWARD,
                on_click=lambda _: collapse(),
                icon_color=ft.Colors.ON_INVERSE_SURFACE,
            ),
            send_btn_top,
        ],
        expand=True,
        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        visible=False,
    )
    container = ft.Container(
        ft.Stack(
            [
                ft.Column([subject_field, button_bar, input_field], expand=False),
                ft.Container(send_btn_bottom, width=40, margin=ft.Margin.only(right=5)),
            ],
            alignment=ft.Alignment.CENTER_RIGHT,
        ),
        bgcolor=ft.Colors.INVERSE_SURFACE,
        margin=ft.Margin.all(5),
        border_radius=20,
    )

    return container
