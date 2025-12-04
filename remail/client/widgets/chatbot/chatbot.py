import flet as ft
from flet.core.colors import Colors
from flet.core.types import FontWeight

from remail.controllers.dtos import LLMResponseDTO
from remail.controllers.llm_controller import LLMController


def create_chatbot():
    llm_controller = LLMController()

    chat_display = ft.ListView(
        expand=True,
        auto_scroll=True,
        spacing=10,
    )
    message_input = ft.TextField(
        label="Type your message...",
        expand=True,
        min_lines=3,
        max_lines=6,
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

    send_button = ft.IconButton(
        "send",
        on_click=send_message,
    )
    input_row = ft.Row(
        controls=[message_input, send_button],
        spacing=10,
    )

    return ft.Column(
        controls=[
            ft.Text("Alfred 🤖", size=24, weight=FontWeight.BOLD),
            chat_display,
            input_row,
        ],
        expand=True,
        spacing=10,
    )
