import flet as ft

from remail.client.state import AppState
from remail.client.widgets.mail_selection import SelectionBar
from remail.controllers.dtos.conversations import ThreadPreviewDTO, ContactDTO
from remail.enums import ContactType

from .state import MainAppState
from ...widgets.chatbot.chatbot import create_chatbot
from ...widgets.thread.thread_list import ThreadList


def create_main_view(page: ft.Page, global_state: AppState):
    main_state = MainAppState()
    main_state.set_displayed([])  # todo
    selection_bar = SelectionBar(main_state)
    chatbot = create_chatbot()
    dashboard = ft.Container(ft.Text("Dashboard (vertrau ist fast fertig)"), bgcolor=ft.Colors.ORANGE, expand=True)
    right_view = ft.Container(dashboard)

    active_user = ContactDTO( #todo
        id=1,
        first_name="John",
        last_name="Doe",
        email="john.doe@example.com",
        is_known=True,
        type=ContactType.PRIVATE
    )

    def on_thread_change(new: ThreadPreviewDTO|None)->None:
        if new:
            current_conversation = next(filter(lambda conv: new in conv.threads, main_state.displayed))
            right_view.content = ThreadList(new, current_conversation, active_user)
        else:
            right_view.content = dashboard
        right_view.update()


    container = ft.Row(expand=True, controls=[
        ft.Column([
            ft.Container(selection_bar, expand=True),
            ft.Container(chatbot, height=400)
        ], width=350),
        right_view])
    return container
