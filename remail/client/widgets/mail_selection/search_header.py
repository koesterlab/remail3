import datetime
from collections.abc import Callable

import flet as ft
from flet.core.control_event import ControlEvent

from remail.client.state.main_app_state import MainAppState, MainAppStateProperties
from remail.controllers.dtos.conversations import ConversationDTO, ThreadPreviewDTO


class SearchHeader(ft.Container):
    def __init__(self, state: MainAppState):
        self.__state = state
        self.__term = state.get(MainAppStateProperties.SEARCH_TERM)

        # ----- Search Input -----
        def handle_change(e: ControlEvent):
            state.set(MainAppStateProperties.SEARCH_TERM, e.control.value)

        self.input = ft.TextField(
            value=self.__term,
            hint_text="Search...",
            on_change=handle_change,
            expand=True,
            color=ft.Colors.ON_SECONDARY,
            border_color="transparent",  # kein Outline
            bgcolor=ft.Colors.SECONDARY,
            border_radius=ft.border_radius.all(30),
            content_padding=ft.padding.symmetric(vertical=6, horizontal=8),
            dense=True,
        )

        def on_search_term_changed(s):
            if s != self.input.value:
                self.input.value = s

        state.register_observer(MainAppStateProperties.SEARCH_TERM, on_search_term_changed)

        def on_home_clicked(_):
            state.set(MainAppStateProperties.SEARCH_TERM, "")
            state.set(MainAppStateProperties.ACTIVE_THREAD, None)
            state.set(MainAppStateProperties.ACTIVE_CONVERSATION, None)
            # todo: load mails from controller

        # ----- Home Icon -----
        home_icon = ft.IconButton(
            icon=ft.Icons.HOME,
            icon_color=ft.Colors.SECONDARY,
            on_click=on_home_clicked,
            icon_size=30,
            style=ft.ButtonStyle(padding=0, bgcolor="transparent"),
        )

        def create_bottom_option(text: str, icon: ft.Icons, callback: Callable[[], None]):
            return ft.Container(
                ft.Row(
                    [
                        ft.Icon(icon, size=18),
                        ft.Text(text, size=15),
                    ]
                ),
                on_click=lambda _: callback(),
            )

        def create_group_from_selected():
            contacts = [
                c
                for e in state.get_selected()
                for c in e.contacts
                if isinstance(e, ConversationDTO)
            ]
            thread = ThreadPreviewDTO(-1, "", 0, 0, "", datetime.datetime.now())
            conversation = ConversationDTO(contacts, [thread], False, None)
            state.set(MainAppStateProperties.ACTIVE_CONVERSATION, conversation)
            state.set(MainAppStateProperties.ACTIVE_THREAD, thread)
            state.clear_selected()

        # ----- unterhalb -----
        archiv_link = create_bottom_option("Archive", ft.Icons.ARCHIVE, lambda: None)
        spam_link = create_bottom_option("Spam", ft.Icons.WARNING, lambda: None)
        delete_button = create_bottom_option("Delete", ft.Icons.DELETE, lambda: None)
        archiv_button = create_bottom_option("Archive", ft.Icons.ARCHIVE, lambda: None)
        group_button = create_bottom_option(
            "Create Group", ft.Icons.GROUP, create_group_from_selected
        )

        bottom_row = ft.Row([], spacing=20, expand=True, height=20)

        def on_selection_change(_):
            selected_count = len(state.get_selected())
            if selected_count == 0:
                bottom_row.controls = [archiv_link, spam_link]
                bottom_row.alignment = ft.MainAxisAlignment.START
            elif selected_count == 1:
                bottom_row.controls = [delete_button, archiv_button, ft.Container()]
                bottom_row.alignment = ft.MainAxisAlignment.SPACE_BETWEEN
            else:
                bottom_row.controls = [delete_button, archiv_button, group_button]
                bottom_row.alignment = ft.MainAxisAlignment.SPACE_BETWEEN
            bottom_row.update()

        state.listen_selection(None, on_selection_change)

        # ----- Layout -----
        content = ft.Column(
            controls=[
                ft.Row([self.input, home_icon], alignment=ft.MainAxisAlignment.START),
                bottom_row,
                ft.Divider(height=3, thickness=2),
            ],
            spacing=5,
        )

        super().__init__(
            content=content,
            padding=2,
            margin=1,
        )
