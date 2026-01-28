import flet as ft

from remail.client.state import AppState
from remail.client.views.dashboard_view import create_dashboard_view
from remail.client.widgets.chatbot.chatbot import create_chatbot
from remail.client.widgets.mail_selection import SelectionBar
from remail.controllers.dtos.conversations import ThreadPreviewDTO
from remail.enums import MainView
from remail.interfaces.email.services.user_service import UserService

from ...state.main_app_state import MainAppState, MainAppStateProperties
from ...widgets.thread.thread_list import ThreadList


def create_main_view(page: ft.Page, global_state: AppState):
    main_state = MainAppState()
    users = UserService.get_all_users()
    if len(users) < 1:
        if global_state.router is not None:
            global_state.router.load_view(MainView.SETTINGS)
        return ft.Container()

    main_state.set(MainAppStateProperties.ACTIVE_USER, users[0])
    main_state.set(
        MainAppStateProperties.DISPLAYED_MAILS,
        list(main_state.conversations_controller.get_conversations(users[0].id)),
    )
    main_state.set(MainAppStateProperties.ACTIVE_CHATBOT, False)
    main_state.set(MainAppStateProperties.ACTIVE_THREAD, None)
    main_state.set(MainAppStateProperties.ACTIVE_CONVERSATION, None)
    main_state.set(MainAppStateProperties.SEARCH_TERM, "")

    selection_bar = SelectionBar(main_state)

    def navigate_to_settings(e):
        if global_state.router:
            page.clean()
            settings_view = global_state.router.load_view(MainView.SETTINGS)
            page.add(settings_view)
            page.update()

    settings_button = ft.IconButton(
        icon=ft.Icons.SETTINGS,
        tooltip="Settings",
        on_click=navigate_to_settings,
    )

    # Replace placeholder columns with real dashboard views
    dashboard = ft.Column(
        [
            ft.Container(
                content=ft.Row(
                    [
                        settings_button,
                    ],
                    alignment=ft.MainAxisAlignment.END,
                ),
                padding=10,
            ),
            create_dashboard_view(page, global_state, users[0].id),
        ],
        expand=True,
    )

    right_view = ft.Container(dashboard, col={"xs": 6, "md": 8, "lg": 9}, expand=True)

    # Chatbot
    chatbot = create_chatbot(main_state)
    chatbot.height = 60
    chatbot.expand = False

    container = ft.ResponsiveRow(
        expand=True,
        controls=[
            ft.Column(
                [ft.Container(selection_bar, expand=1), chatbot], col={"xs": 6, "md": 4, "lg": 3}
            ),
            right_view,
        ],
    )

    def on_thread_change(new: ThreadPreviewDTO | None) -> None:
        print("ACTIVE_THREAD changed:", new)
        if new:
            right_view.content = ThreadList(main_state)
        else:
            right_view.content = dashboard
        right_view.update()

    def on_chatbot_state_change(is_active: bool) -> None:
        if is_active:
            chatbot.expand = 4
        else:
            chatbot.expand = False
            chatbot.height = 60
        container.update()

    main_state.register_observer(MainAppStateProperties.ACTIVE_CHATBOT, on_chatbot_state_change)
    main_state.register_observer(MainAppStateProperties.ACTIVE_THREAD, on_thread_change)

    return container
