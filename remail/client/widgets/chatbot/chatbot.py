import flet as ft
from flet.core.colors import Colors

from remail.client.state.main_app_state import MainAppState, MainAppStateProperties
from remail.controllers.dtos import LLMResponseDTO
from remail.controllers.dtos.user_dto import UserDTO
from remail.controllers.llm_controller import LLMController
from remail.interfaces.llm.chat_service import ChatService
from remail.interfaces.llm.enums.llm_message_role import LLMMessageRole


def create_chatbot(app_state: MainAppState):
    llm_controller = LLMController()
    chat_service = ChatService()

    # if score is above zero, the widget is "active" and expands
    _active_input = False
    _active_hover = False

    def change_active_state(
        active_input: bool | None = None, active_hover: bool | None = None
    ) -> None:
        nonlocal _active_input, _active_hover
        if active_input is not None:
            _active_input = active_input
        if active_hover is not None:
            _active_hover = active_hover

        app_state.set(MainAppStateProperties.ACTIVE_CHATBOT, _active_input or _active_hover)

    chat_display = ft.ListView(
        expand=True,
        auto_scroll=True,
        spacing=10,
        visible=False,
    )

    header_text = ft.Text(
        "Select a thread to chat about it",
        size=14,
        color=ft.Colors.ON_SURFACE_VARIANT,
    )

    def change_chat_visibility(visible: bool) -> None:
        nonlocal chat_display
        chat_display.visible = visible
        chat_display.update()

    app_state.register_observer(MainAppStateProperties.ACTIVE_CHATBOT, change_chat_visibility)

    def _update_controls(*controls: ft.Control) -> None:
        for control in controls:
            if getattr(control, "page", None):
                control.update()

    message_input = ft.TextField(
        label="Call AIfred 🤖 ...",
        expand=True,
        min_lines=1,
        max_lines=6,
        on_focus=lambda _: change_active_state(active_input=True),
        on_blur=lambda _: change_active_state(active_input=False),
        color=ft.Colors.ON_PRIMARY,
    )

    default_label = message_input.label

    def _render_chat_history(thread) -> None:
        chat_display.controls.clear()

        if thread is None:
            header_text.value = "Select a thread to chat about it"
            message_input.disabled = True
            message_input.label = "Select a thread to chat about it"
            _update_controls(chat_display, header_text, message_input)
            return

        active_user: UserDTO | None = app_state.get(MainAppStateProperties.ACTIVE_USER)
        if active_user is None:
            header_text.value = "Select a thread to chat about it"
            message_input.disabled = True
            message_input.label = "Select a thread to chat about it"
            _update_controls(chat_display, header_text, message_input)
            return

        header_text.value = f"Chatting about: {thread.title}"
        message_input.disabled = False
        message_input.label = default_label

        chat_session = chat_service.get_or_create_session(active_user.id, thread.thread_id)
        if chat_session.id is None:
            _update_controls(chat_display, header_text, message_input)
            return

        messages = chat_service.get_session_messages(chat_session.id)
        for msg in messages:
            if msg.role == LLMMessageRole.USER:
                prefix = "You"
                color = Colors.BLUE
            elif msg.role == LLMMessageRole.ASSISTANT:
                prefix = "AI"
                color = Colors.GREEN
            else:
                prefix = "System"
                color = Colors.WHITE

            chat_display.controls.append(ft.Text(f"{prefix}: {msg.content}", color=color))
        _update_controls(chat_display, header_text, message_input)

    app_state.register_observer(MainAppStateProperties.ACTIVE_THREAD, _render_chat_history)

    def _get_ai_response(user_message: str) -> LLMResponseDTO | None:
        """Get AI response using LLM controller with chat memory.

        Args:
            user_message: The user's message

        Returns:
            LLMResponseDTO or None if an error occurred
        """

        active_thread = app_state.get(MainAppStateProperties.ACTIVE_THREAD)
        active_user: UserDTO | None = app_state.get(MainAppStateProperties.ACTIVE_USER)
        if active_thread is None or active_user is None:
            return None

        try:
            response_dto: LLMResponseDTO = llm_controller.chat(
                prompt=user_message,
                user_id=active_user.id,
                thread_id=active_thread.thread_id,
                max_tokens=100,
                temperature=0.7,
            )

            return response_dto

        except Exception:
            return None

    def send_message(e) -> None:
        active_thread = app_state.get(MainAppStateProperties.ACTIVE_THREAD)
        if active_thread is None:
            return

        user_message = message_input.value.strip()

        if not user_message:
            return

        message_input.value = ""
        message_input.update()

        chat_display.controls.append(ft.Text(f"You: {user_message}", color=Colors.BLUE))

        loading_indicator = ft.ProgressRing()
        loading_container = ft.Row(
            controls=[loading_indicator, ft.Text("AIfred is thinking...", color=Colors.YELLOW_500)],
            spacing=10,
        )

        chat_display.controls.append(loading_container)
        chat_display.update()

        response_dto = _get_ai_response(user_message)
        chat_display.controls.remove(loading_container)

        if response_dto is None:
            chat_display.controls.append(
                ft.Text(
                    f"AI: (LLM Server Unavailable) I received your message: '{user_message}'. Please make sure the LLM server is running at the configured base URL.",
                    color=Colors.RED,
                )
            )

        else:
            chat_display.controls.append(ft.Text(f"AI: {response_dto.content}", color=Colors.GREEN))

        chat_display.update()

    message_input.on_submit = send_message

    input_row = ft.Row(
        controls=[message_input],
        spacing=10,
        height=50,
    )

    _render_chat_history(app_state.get(MainAppStateProperties.ACTIVE_THREAD))

    return ft.Container(
        ft.Column(
            controls=[
                header_text,
                # ft.Text("Alfred 🤖", size=24, weight=FontWeight.BOLD),
                chat_display,
                input_row,
            ],
            spacing=10,
            alignment=ft.MainAxisAlignment.END,
        ),
        on_hover=lambda f: change_active_state(active_hover=f.data == "true"),
        padding=ft.padding.all(5),
        bgcolor=ft.Colors.SURFACE_CONTAINER_HIGHEST,
    )
