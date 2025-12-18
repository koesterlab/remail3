import flet as ft

from remail.client.state import AppState
from remail.client.widgets.mail_selection import SelectionBar
from remail.controllers.dtos.conversations import ContactDTO, ThreadPreviewDTO
from remail.enums import ContactType
from tests.client.views.main.test_data_conversations import create_test_data

from ...state.main_app_state import MainAppState, MainAppStateProperties
from ...widgets.chatbot.chatbot import create_chatbot
from ...widgets.thread.thread_list import ThreadList


def create_main_view(page: ft.Page, global_state: AppState):
    main_state = MainAppState()
    main_state.set(MainAppStateProperties.DISPLAYED_MAILS, create_test_data())  # todo
    main_state.set(MainAppStateProperties.ACTIVE_CHATBOT, False)
    main_state.set(MainAppStateProperties.ACTIVE_THREAD, None)
    main_state.set(MainAppStateProperties.SEARCH_TERM, "")
    selection_bar = SelectionBar(main_state)
    dashboard = ft.Container(
        ft.Text("Dashboard (vertrau ist fast fertig)"), bgcolor=ft.Colors.ORANGE, expand=True
    )
    right_view = ft.Container(dashboard, col={"xs": 6, "md": 8, "lg": 9}, expand=True)

    active_user = ContactDTO(  # todo
        id=1,
        first_name="John",
        last_name="Doe",
        email="john.doe@example.com",
        is_known=True,
        type=ContactType.PRIVATE,
    )

    main_state.set(MainAppStateProperties.ACTIVE_USER, active_user)

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

    thread_list = ThreadList(main_state)

    def on_thread_change(new: ThreadPreviewDTO | None) -> None:
        if new:
            right_view.content = thread_list
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
