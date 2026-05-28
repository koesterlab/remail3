import flet as ft

from remail.client.state.main_app_state import MainAppState, MainAppStateProperties
from remail.controllers.dtos import LLMResponseDTO
from remail.controllers.llm_controller import LLMController
from remail.controllers.settings_controller import SettingsController


def create_chatbot(app_state: MainAppState):
    settings = SettingsController().get_settings()
    llm_controller = LLMController(settings.llm_url, settings.llm_key)

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
        auto_scroll=True,
        spacing=10,
        height=0,
        clip_behavior=ft.ClipBehavior.HARD_EDGE,
    )

    def change_chat_visibility(visible: bool) -> None:

        has_messages = len(chat_display.controls) > 0
        chat_display.height = 290 if (visible and has_messages) else 0
        chat_display.update()

    app_state.register_observer(MainAppStateProperties.ACTIVE_CHATBOT, change_chat_visibility)

    def _on_focus(_) -> None:
        change_active_state(active_input=True)

    def _on_blur(_) -> None:
        change_active_state(active_input=False)

    def _on_hover(f) -> None:
        change_active_state(active_hover=f.data == "true")

    message_input = ft.TextField(
        label="Call AIfred 🤖 ...",
        expand=True,
        min_lines=1,
        max_lines=6,
        on_focus=_on_focus,
        on_blur=_on_blur,
        color=ft.Colors.WHITE,
        label_style=ft.TextStyle(color=ft.Colors.WHITE70),
        cursor_color=ft.Colors.WHITE,
    )

    def _get_ai_response(user_message: str) -> LLMResponseDTO | None:
        """Get AI response using LLM controller with chat memory.

        Args:
            user_message: The user's message

        Returns:
            LLMResponseDTO or None if an error occurred
        """

        try:
            response_dto: LLMResponseDTO = llm_controller.chat(
                prompt=user_message,
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

        chat_display.controls.append(ft.Text(f"You: {user_message}", color=ft.Colors.BLUE))

        if chat_display.height == 0:
            chat_display.height = 290

        loading_indicator = ft.ProgressRing()
        loading_container = ft.Row(
            controls=[
                loading_indicator,
                ft.Text("AIfred is thinking...", color=ft.Colors.YELLOW_500),
            ],
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
                    color=ft.Colors.RED,
                )
            )

        else:
            chat_display.controls.append(
                ft.Text(f"AI: {response_dto.content}", color=ft.Colors.GREEN)
            )

        chat_display.update()

    message_input.on_submit = send_message

    input_row = ft.Row(
        controls=[message_input],
        spacing=10,
    )

    container = ft.Container(
        ft.Column(
            controls=[chat_display, input_row],
            spacing=10,
            tight=True,
        ),
        on_hover=_on_hover,
        padding=ft.Padding.all(5),
        bgcolor=ft.Colors.SURFACE_CONTAINER_HIGHEST,
    )
    return container
