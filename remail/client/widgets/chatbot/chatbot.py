import flet as ft
from flet.core.colors import Colors

from remail.client.state.main_app_state import MainAppState, MainAppStateProperties
from remail.controllers.dtos import LLMResponseDTO
from remail.controllers.dtos.conversations import ThreadPreviewDTO
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

    header_text = ft.Text(
        "Select a thread to chat about it",
        size=12,
        color=Colors.ON_SURFACE_VARIANT,
    )

    header_container = ft.Container(
        content=header_text,
        padding=ft.padding.symmetric(horizontal=8, vertical=6),
        bgcolor=ft.Colors.SURFACE,
        visible=False,
    )

    chat_display = ft.ListView(
        expand=True,
        auto_scroll=True,
        spacing=10,
        visible=False,
    )

    def change_chat_visibility(visible: bool) -> None:
        nonlocal chat_display
        chat_display.visible = visible
        header_container.visible = visible
        chat_display.update()
        header_container.update()

    app_state.register_observer(MainAppStateProperties.ACTIVE_CHATBOT, change_chat_visibility)

    message_input = ft.TextField(
        label="Select a thread to chat about it",
        expand=True,
        min_lines=1,
        max_lines=6,
        on_focus=lambda _: change_active_state(active_input=True),
        on_blur=lambda _: change_active_state(active_input=False),
        color=ft.Colors.ON_PRIMARY,
        disabled=True,
    )

    def _get_active_context() -> tuple[int, int] | None:
        active_thread: ThreadPreviewDTO | None = app_state.get(
            MainAppStateProperties.ACTIVE_THREAD
        )
        active_user = app_state.get(MainAppStateProperties.ACTIVE_USER)
        if not active_thread or not active_user:
            return None
        return active_user.id, active_thread.thread_id

    def _render_session_messages(active_thread: ThreadPreviewDTO | None) -> None:
        chat_display.controls.clear()

        if not active_thread:
            header_text.value = "Select a thread to chat about it"
            message_input.label = "Select a thread to chat about it"
            message_input.disabled = True
            chat_display.controls.append(
                ft.Text(
                    "Select a thread to chat about it.",
                    color=Colors.ON_SURFACE_VARIANT,
                )
            )
            chat_display.update()
            header_container.update()
            message_input.update()
            return

        header_text.value = f"Chatting about: {active_thread.title}"
        message_input.label = "Ask Alfred about this thread..."
        message_input.disabled = False

        active_user = app_state.get(MainAppStateProperties.ACTIVE_USER)
        if not active_user:
            message_input.disabled = True
            chat_display.controls.append(
                ft.Text(
                    "No active user available.",
                    color=Colors.ON_SURFACE_VARIANT,
                )
            )
            chat_display.update()
            header_container.update()
            message_input.update()
            return

        history = llm_controller.get_session_messages(
            user_id=active_user.id, thread_id=active_thread.thread_id
        )

        for message in history:
            if message.role == LLMMessageRole.USER:
                chat_display.controls.append(
                    ft.Text(f"You: {message.content}", color=Colors.BLUE)
                )
            elif message.role == LLMMessageRole.ASSISTANT:
                chat_display.controls.append(
                    ft.Text(f"AI: {message.content}", color=Colors.GREEN)
                )

        chat_display.update()
        header_container.update()
        message_input.update()

    def _get_ai_response(user_message: str) -> LLMResponseDTO | None:
        """Get AI response using LLM controller with chat memory.

        Args:
            user_message: The user's message

        Returns:
            LLMResponseDTO or None if an error occurred
        """

        try:
            active_context = _get_active_context()
            if not active_context:
                return None
            user_id, thread_id = active_context

            response_dto = llm_controller.chat(
                prompt=user_message,
                thread_id=thread_id,
                user_id=user_id,
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

        message_input.value = ""
        message_input.update()

        chat_display.controls.append(ft.Text(f"You: {user_message}", color=Colors.BLUE))

        loading_indicator = ft.ProgressRing()
        loading_container = ft.Row(
            controls=[loading_indicator, ft.Text("Alfred is thinking...", color=Colors.YELLOW_500)],
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

    app_state.register_observer(
        MainAppStateProperties.ACTIVE_THREAD, _render_session_messages
    )
    _render_session_messages(app_state.get(MainAppStateProperties.ACTIVE_THREAD))

    return ft.Container(
        ft.Column(
            controls=[
                header_container,
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
