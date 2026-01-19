import flet as ft
from flet.core.colors import Colors

from remail.client.state.main_app_state import MainAppState, MainAppStateProperties
from remail.controllers.dtos import LLMResponseDTO
from remail.controllers.llm_controller import LLMController
from remail.interfaces.llm.enums.llm_message_role import LLMMessageRole


def create_chatbot(app_state: MainAppState):
    llm_controller = LLMController()

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

    def change_chat_visibility(visible: bool) -> None:
        nonlocal chat_display
        chat_display.visible = visible
        chat_display.update()

    app_state.register_observer(MainAppStateProperties.ACTIVE_CHATBOT, change_chat_visibility)

    thread_header = ft.Text(
        value="No thread selected",
        size=12,
        color=Colors.GREY_500,
    )

    empty_state = ft.Text(
        value="Select a thread to chat about it",
        size=12,
        color=Colors.GREY_500,
        visible=False,
    )

    message_input = ft.TextField(
        label="Call AIfred 🤖 ...",
        expand=True,
        min_lines=1,
        max_lines=6,
        on_focus=lambda _: change_active_state(active_input=True),
        on_blur=lambda _: change_active_state(active_input=False),
        color=ft.Colors.ON_PRIMARY,
    )

    def _render_message(role: LLMMessageRole, content: str) -> ft.Text:
        if role == LLMMessageRole.USER:
            return ft.Text(f"You: {content}", color=Colors.BLUE)

        if role == LLMMessageRole.ASSISTANT:
            return ft.Text(f"AI: {content}", color=Colors.GREEN)

        return ft.Text(f"{role.value}: {content}", color=Colors.ON_SURFACE)

    def _get_active_thread():
        return app_state.get(MainAppStateProperties.ACTIVE_THREAD)

    def _get_active_user():
        return app_state.get(MainAppStateProperties.ACTIVE_USER)

    def _safe_update(control: ft.Control) -> None:
        if getattr(control, "page", None) is not None:
            control.update()

    def _get_ai_response(user_message: str) -> LLMResponseDTO | None:
        """Get AI response using LLM controller with chat memory.

        Args:
            user_message: The user's message

        Returns:
            LLMResponseDTO or None if an error occurred
        """

        thread = _get_active_thread()
        user = _get_active_user()

        if thread is None or user is None:
            return None

        try:
            response_dto: LLMResponseDTO = llm_controller.chat(
                prompt=user_message,
                user_id=user.id,
                thread_id=thread.thread_id,
                max_tokens=100,
                temperature=0.7,
            )

            return response_dto

        except Exception:
            return None

    def send_message(e) -> None:
        user_message = message_input.value.strip()

        if not user_message:
            return

        thread = _get_active_thread()
        user = _get_active_user()

        if thread is None or user is None:
            return

        message_input.value = ""
        message_input.update()

        chat_display.controls.append(_render_message(LLMMessageRole.USER, user_message))

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
            chat_display.controls.append(
                _render_message(LLMMessageRole.ASSISTANT, response_dto.content)
            )

        chat_display.update()

    message_input.on_submit = send_message

    input_row = ft.Row(
        controls=[message_input],
        spacing=10,
        height=50,
    )

    def refresh_thread_messages(thread) -> None:
        user = _get_active_user()
        has_thread = thread is not None

        thread_header.value = f"Thread: {thread.title}" if has_thread else "No thread selected"
        empty_state.visible = not has_thread
        message_input.disabled = not has_thread

        chat_display.controls.clear()

        if has_thread and user is not None:
            messages = llm_controller.get_session_messages(user.id, thread.thread_id)

            for msg in messages:
                chat_display.controls.append(_render_message(msg.role, msg.content))

        _safe_update(thread_header)
        _safe_update(empty_state)
        _safe_update(message_input)
        _safe_update(chat_display)

    app_state.register_observer(MainAppStateProperties.ACTIVE_THREAD, refresh_thread_messages)

    refresh_thread_messages(_get_active_thread())

    return ft.Container(
        ft.Column(
            controls=[
                # ft.Text("Alfred 🤖", size=24, weight=FontWeight.BOLD),
                thread_header,
                empty_state,
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
