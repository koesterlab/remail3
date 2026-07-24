import flet as ft

from remail import errors as ee
from remail.client.state import MainAppState, MainAppStateProperties
from remail.controllers.dtos.conversations import ConversationDTO, ThreadPreviewDTO
from remail.controllers.llm_controller import LLMController
from remail.controllers.settings_controller import SettingsController


def create_new_message_dialog(state: MainAppState) -> ft.Container:
    expanded = False

    def safe_update(control: ft.Control) -> None:
        try:
            control.update()
        except RuntimeError:
            # Control may be stale or not mounted yet (observer outlives dialog instance).
            return

    active_thread = state.get(MainAppStateProperties.ACTIVE_THREAD)
    needs_subject = active_thread and active_thread.thread_id < 0 and not active_thread.title

    def expand() -> None:
        nonlocal expanded
        expanded = True
        input_field.max_lines = 10
        input_field.min_lines = 10
        input_field.dense = False
        safe_update(input_field)
        button_bar.visible = True
        safe_update(button_bar)
        send_btn_bottom.visible = False
        safe_update(send_btn_bottom)

    def collapse() -> None:
        nonlocal expanded
        expanded = False
        input_field.max_lines = 1
        input_field.min_lines = 1
        input_field.dense = True
        safe_update(input_field)
        button_bar.visible = False
        safe_update(button_bar)
        send_btn_bottom.visible = True
        safe_update(send_btn_bottom)

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
        safe_update(send_btn_top)
        safe_update(send_btn_bottom)

    def on_draft_change(s):
        input_field.value = s
        if not expanded:
            expand()
        on_change()

    def generate_ai_reply() -> None:
        thread_preview = state.get(MainAppStateProperties.ACTIVE_THREAD)
        if thread_preview is None or thread_preview.thread_id < 0:
            return

        full_thread = state.thread_controller.get_thread(thread_preview.thread_id)
        if full_thread is None or not full_thread.messages:
            return

        last_message_body = full_thread.messages[-1].content.body

        settings = SettingsController().get_settings()
        llm = LLMController(settings.llm_url, settings.llm_key)
        result = llm.generate_reply(last_message_body)

        state.set(MainAppStateProperties.DRAFT, result.content)

    def send_mail():
        thread = state.get(MainAppStateProperties.ACTIVE_THREAD)
        conversation = state.get(MainAppStateProperties.ACTIVE_THREAD_CONVERSATION)
        if not thread or not conversation:
            return
        subject = thread.title or subject_field.value
        if not subject:
            return
        message = input_field.value
        if not message:
            return

        previous_thread_id = thread.thread_id

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
            sent_message = state.thread_controller.send_message(thread_id, message, [])
        except ee.EmailError:
            from remail.client import show_snack_bar

            show_snack_bar(
                ft.Text("Failed to send message. Please check your connection and try again.")
            )
            return

        updated_thread = ThreadPreviewDTO(
            thread_id=thread_id,
            title=subject,
            total_count=thread.total_count + 1,
            unread_count=thread.unread_count,
            last_message=sent_message.content.body,
            last_message_datetime=sent_message.sent_at,
        )

        updated_threads: list[ThreadPreviewDTO] = []
        replaced = False
        for thread_preview in conversation.threads:
            if thread_preview.thread_id == previous_thread_id:
                updated_threads.append(updated_thread)
                replaced = True
            else:
                updated_threads.append(thread_preview)
        if not replaced:
            updated_threads.append(updated_thread)

        updated_conversation = ConversationDTO(
            id=conversation.id,
            contacts=conversation.contacts,
            threads=updated_threads,
            is_favorite=conversation.is_favorite,
            custom_name=conversation.custom_name,
        )

        state.set(MainAppStateProperties.ACTIVE_THREAD_CONVERSATION, updated_conversation)
        state.set(MainAppStateProperties.ACTIVE_THREAD, updated_thread)

        # clear
        state.set(MainAppStateProperties.DRAFT, "")
        input_field.value = ""
        on_change()
        safe_update(input_field)

    state.register_observer(MainAppStateProperties.DRAFT, on_draft_change, weak=True)
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

    generate_btn = ft.IconButton(
        ft.Icons.AUTO_AWESOME,
        on_click=lambda _: generate_ai_reply(),
        icon_color=ft.Colors.ON_INVERSE_SURFACE,
        tooltip="Generate AI reply",
    )

    button_bar = ft.Row(
        [
            ft.IconButton(
                ft.Icons.ARROW_DOWNWARD,
                on_click=lambda _: collapse(),
                icon_color=ft.Colors.ON_INVERSE_SURFACE,
            ),
            generate_btn,
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
