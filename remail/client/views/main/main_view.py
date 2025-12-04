import flet as ft

from remail.client.state import AppState
from remail.client.widgets.mail_selection import SelectionBar

from .state import MainAppState


def create_main_view(page: ft.Page, state_: AppState):
    state = MainAppState()
    state.set_displayed([])  # todo
    selection_bar = SelectionBar(state)
    thread_view = ft.Container(bgcolor=ft.Colors.ORANGE, expand=True)
    container = ft.Row(expand=True, controls=[selection_bar, thread_view])
    return container
