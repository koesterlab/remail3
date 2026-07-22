# remail/client/widgets/dashboard/ai_summary.py
from __future__ import annotations

import flet as ft

from remail.client.state import MainAppState, MainAppStateProperties
from remail.controllers.dtos.user_dto import UserDTO
from remail.controllers.llm_controller import LLMController
from remail.controllers.settings_controller import SettingsController
from remail.interfaces.email.services.dashboard_service import DashboardService


class AiSummary(ft.Container):
    """
    Dashboard widget that shows a short AI-generated overview of the user's
    new (unread) emails.

    The AI call can take a few seconds and must not freeze the UI, so the
    actual work runs in a background thread (started in ``did_mount``) and the
    text is updated once the result arrives.
    """

    def __init__(self, state: MainAppState) -> None:
        self.state = state

        # The single Text control we update once the summary is ready.
        self._summary_text = ft.Text(
            "",
            size=16,
            color=ft.Colors.ON_SURFACE_VARIANT,
            selectable=True,
        )

        # Loading row shown while the AI is working.
        self._loading = ft.Row(
            spacing=10,
            controls=[
                ft.ProgressRing(width=18, height=18, stroke_width=2),
                ft.Text(
                    "Generating your overview...",
                    size=16,
                    color=ft.Colors.ON_SURFACE_VARIANT,
                ),
            ],
        )

        super().__init__(
            padding=0,
            content=ft.Column(
                spacing=8,
                controls=[self._loading, self._summary_text],
            ),
        )

    def did_mount(self) -> None:
        """Called by Flet once the control is on the page: start loading."""
        # self.page is available here. run_thread keeps the UI responsive.
        self.page.run_thread(self._load_summary)  # type: ignore[attr-defined]
    def _load_summary(self) -> None:
        """Fetch unread emails, ask the AI for an overview, update the UI."""
        try:
            user: UserDTO = self.state.get(MainAppStateProperties.ACTIVE_USER)
            emails = DashboardService.get_unread_emails_for_user(user.id)

            settings = SettingsController().get_settings()
            llm_controller = LLMController(settings.llm_url, settings.llm_key)

            response = llm_controller.summarize_emails(emails)
            self._show(response.content)
        except Exception:
            # Most likely the local LLM server (Ollama) is not running.
            self._show(
                "Could not generate an overview right now. "
                "Please make sure the local AI server is running.",
                is_error=True,
            )

    def _show(self, text: str, is_error: bool = False) -> None:
        """Replace the loading indicator with the final text."""
        self._loading.visible = False
        self._summary_text.value = text
        self._summary_text.color = ft.Colors.ERROR if is_error else ft.Colors.ON_SURFACE_VARIANT
        self.update()
