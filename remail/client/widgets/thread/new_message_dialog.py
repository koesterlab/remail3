import flet as ft

from remail.client.state import MainAppState, MainAppStateProperties


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
        # Retrieve the current thread and conversation from state
        thread = state.get(MainAppStateProperties.ACTIVE_THREAD)
        conversation = state.get(MainAppStateProperties.ACTIVE_THREAD_CONVERSATION)
        if thread.title == "":
            return
        message = input_field.value

        # Clear the draft immediately so the user can type again
        state.set(MainAppStateProperties.DRAFT, "")

        # Disable the send buttons while sending to prevent double-sending
        send_btn_top.disabled = True
        send_btn_bottom.disabled = True
        send_btn_top.update()
        send_btn_bottom.update()

        # Run the send operation in the background so the UI doesn't freeze
        # Without async, sending via SMTP can take 3-5 seconds and freeze the UI
        async def do_send():
            try:
                if conversation.id < 0:  # creating new conversation
                    conv = state.get_active_email_account().create_conversation(
                        conversation.contacts
                    )
                    t = state.thread_controller.create_thread(conv, thread.title)
                elif thread.id < 0:
                    t = state.thread_controller.create_thread(conversation, thread.title)
                else:
                    t = thread
                # Send the message via SMTP in the background
                state.thread_controller.send_message(t, message, [])
            except Exception:
                pass  # nosec

        # Start sending in the background using Flet's task system
        container.page.run_task(do_send)

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
                ft.Container(send_btn_bottom, width=40, margin=ft.Margin.only(right=5)),
            ],
            alignment=ft.Alignment.CENTER_RIGHT,
        ),
        bgcolor=ft.Colors.INVERSE_SURFACE,
        margin=ft.Margin.all(5),
        border_radius=20,
    )

    return container