import flet as ft

from remail.client.state import MainAppState, MainAppStateProperties
from remail.client.views.main import EmailView

from .settings import SettingsView


class IndexView(ft.Container):
    def __init__(self) -> None:
        super().__init__(expand=True)

    def start(self) -> None:
        state = MainAppState()
        state.set(MainAppStateProperties.DISPLAYED_MAILS, [])
        state.set(MainAppStateProperties.ACTIVE_CHATBOT, False)
        state.set(MainAppStateProperties.ACTIVE_ATTACHMENTS, False)
        state.set(MainAppStateProperties.ACTIVE_THREAD, None)
        state.set(MainAppStateProperties.ACTIVE_CONVERSATION, None)
        state.set(MainAppStateProperties.ACTIVE_THREAD_CONVERSATION, None)
        state.set(MainAppStateProperties.SEARCH_TERM, "")
        state.set(MainAppStateProperties.SORT_BY_DATE, False)
        state.set(MainAppStateProperties.ACTIVE_SETTINGS, None)

        settings_view = SettingsView(state)
        emails_view = EmailView(state)

        def show_content(settings: bool) -> None:
            self.content = settings_view if settings else emails_view
            try:
                self.update()
            except Exception:
                pass  # nosec

        state.register_observer(
            MainAppStateProperties.ACTIVE_SETTINGS, lambda s: show_content(s is not None)
        )
        show_content(False)
        emails_view.run_sync_threads()
