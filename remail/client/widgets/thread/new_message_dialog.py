import flet as ft

from remail.client.state import MainAppState, MainAppStateProperties
from remail.controllers import EmailController


def create_new_message_dialog(state: MainAppState) -> ft.Container:
    expanded = False

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
        # retrieve data
        thread = state.get(MainAppStateProperties.ACTIVE_THREAD)
        conversation = state.get(MainAppStateProperties.ACTIVE_CONVERSATION)
        if thread.title == "":
            return
        message = input_field.value

        # send
        controller = EmailController.from_id(state.get(MainAppStateProperties.ACTIVE_USER).id)
        if conversation.id < 0:  # creating new conversation
            controller.send_email_new_conversation(
                [c.id for c in conversation.contacts], thread.title, message, None
            )
        elif thread.id < 0:
            controller.send_email_new_thread(thread.title, message, conversation.id, None)
        else:
            controller.send_email(thread.title, message, None, thread.id)

        # clear
        state.set(MainAppStateProperties.DRAFT, "")

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
                ft.Column([button_bar, input_field], expand=False),
                ft.Container(send_btn_bottom, width=40, margin=ft.margin.only(right=5)),
            ],
            alignment=ft.alignment.center_right,
        ),
        bgcolor=ft.Colors.INVERSE_SURFACE,
        margin=ft.margin.all(5),
        border_radius=20,
    )

    return container
