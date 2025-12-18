"""Chatbot view for interacting with AI using email thread context."""

import flet as ft

from remail.client.state.app_state import AppState
from remail.controllers.llm_controller import LLMController


def create_chatbot_view(page: ft.Page, app_state: AppState) -> ft.Container:
    """Create the chatbot view.

    Args:
        page: The Flet page
        app_state: Application state containing active thread

    Returns:
        Container with chatbot UI
    """

    # Controllers
    llm_controller = LLMController()

    # UI State
    messages_display = ft.Column(
        spacing=10,
        auto_scroll=True,
    )

    # Store session ID locally
    current_session_id: int | None = None

    def load_chat_history() -> None:
        """Load and display chat history for current session."""
        nonlocal current_session_id

        if not app_state.active_thread:
            messages_display.controls.clear()
            return

        # Note: In a real implementation, you would fetch the session and messages
        # from the database using ChatService. For now, this is a placeholder.
        # messages = chat_service.get_session_messages(current_session_id)
        # for msg in messages:
        #     add_message_to_display(msg.role, msg.content)

        page.update()

    def add_message_to_display(role: str, content: str) -> None:
        """Add a message to the display.

        Args:
            role: "user" or "assistant"
            content: Message content
        """
        alignment = ft.MainAxisAlignment.END if role == "user" else ft.MainAxisAlignment.START
        bg_color = ft.Colors.BLUE_200 if role == "user" else ft.Colors.GREY_300
        text_color = ft.Colors.BLACK if role == "user" else ft.Colors.BLACK

        message_bubble = ft.Container(
            ft.Text(
                content,
                size=12,
                color=text_color,
                selectable=True,
            ),
            bgcolor=bg_color,
            padding=10,
            border_radius=8,
            width=page.window_width * 0.6 if page.window_width else 400,
        )

        message_row = ft.Row(
            [message_bubble],
            alignment=alignment,
        )

        messages_display.controls.append(message_row)
        page.update()

    def send_message(e: ft.ControlEvent) -> None:
        """Handle sending a message.

        Args:
            e: Control event
        """
        nonlocal current_session_id

        if not app_state.active_thread:
            show_error_snackbar("No thread selected")
            return

        message_content = message_input.value.strip()
        if not message_content:
            return

        # Display user message
        add_message_to_display("user", message_content)

        # Clear input
        message_input.value = ""
        message_input.focus()

        # Show loading indicator
        send_button.disabled = True
        page.update()

        try:
            # Generate response with thread context
            # Note: In a real implementation, pass the current user_id
            result = llm_controller.chat_with_thread_context(
                user_id=1,  # Placeholder: should come from authenticated user
                thread_id=app_state.active_thread,
                user_message=message_content,
            )

            if result["status"] == "success":
                current_session_id = result.get("session_id")
                assistant_message = result.get("completion", "No response")
                add_message_to_display("assistant", assistant_message)
            else:
                show_error_snackbar(result.get("message", "Failed to generate response"))

        except Exception as ex:
            show_error_snackbar(f"Error: {str(ex)}")

        finally:
            send_button.disabled = False
            page.update()

    def show_error_snackbar(message: str) -> None:
        """Show error message.

        Args:
            message: Error message
        """
        snackbar = ft.SnackBar(
            ft.Text(message),
        )
        page.snack_bar = snackbar
        snackbar.open = True
        page.update()

    def on_thread_changed() -> None:
        """Handle thread selection change."""
        messages_display.controls.clear()
        load_chat_history()

    # Input components
    message_input = ft.TextField(
        label="Type your message",
        multiline=True,
        min_lines=1,
        max_lines=4,
        filled=True,
        expand=True,
    )

    send_button = ft.IconButton(
        icon=ft.Icons.SEND,
        icon_size=20,
        tooltip="Send message",
        on_click=send_message,
    )

    # Header showing thread info
    thread_header = ft.Container(
        ft.Column(
            [
                ft.Text(
                    "AI Chat Assistant",
                    size=18,
                    weight=ft.FontWeight.BOLD,
                ),
                ft.Text(
                    (
                        f"Thread #{app_state.active_thread}"
                        if app_state.active_thread
                        else "Select a thread to chat"
                    ),
                    size=12,
                    color=ft.Colors.GREY_700,
                ),
            ],
            spacing=5,
        ),
        padding=10,
        bgcolor=ft.Colors.LIGHT_BLUE_50,
        border_radius=5,
    )

    # No thread selected message
    no_thread_message = ft.Container(
        ft.Column(
            [
                ft.Icon(
                    name=ft.Icons.INFO,
                    size=48,
                    color=ft.Colors.GREY_600,
                ),
                ft.Text(
                    "Select a thread to chat about it",
                    size=14,
                    color=ft.Colors.GREY_700,
                    text_align=ft.TextAlign.CENTER,
                ),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=10,
        ),
        expand=True,
        alignment=ft.alignment.center,
    )

    # Input area with conditional visibility
    input_area = ft.Container(
        ft.Row(
            [message_input, send_button],
            spacing=10,
        ),
        padding=10,
        visible=bool(app_state.active_thread),
    )

    # Main layout
    main_column = ft.Column(
        [
            thread_header,
            ft.Divider(height=1),
            ft.Container(
                messages_display,
                expand=True,
                padding=10,
            ),
            ft.Divider(height=1),
            input_area if app_state.active_thread else no_thread_message,
        ],
        expand=True,
    )

    return ft.Container(
        main_column,
        expand=True,
        padding=10,
        border_radius=10,
    )
