import datetime
from collections.abc import Callable

import flet as ft

from remail.client.state.main_app_state import MainAppState, MainAppStateProperties
from remail.controllers.dtos.conversations import ConversationDTO, ThreadPreviewDTO


class SearchHeader(ft.Container):
    def __init__(self, state: MainAppState):
        self.__state = state
        self.__term = state.get(MainAppStateProperties.SEARCH_TERM)

        all_mails = []

        # ----- Search Input -----
        def handle_change():
            state.set(MainAppStateProperties.SEARCH_TERM, self.input.value)

        self.input = ft.TextField(
            value=self.__term,
            hint_text="Search...",
            on_change=handle_change,
            expand=True,
            color=ft.Colors.ON_SECONDARY,
            border_color="transparent",
            bgcolor=ft.Colors.SECONDARY,
            border_radius=ft.BorderRadius.all(30),
            content_padding=ft.Padding.symmetric(vertical=6, horizontal=8),
            dense=True,
        )

        def on_search_term_changed(s):
            if s != self.input.value:
                self.input.value = s

        state.register_observer(MainAppStateProperties.SEARCH_TERM, on_search_term_changed)

        def on_home_clicked(_):
            state.set(MainAppStateProperties.SEARCH_TERM, "")
            state.set(MainAppStateProperties.ACTIVE_THREAD, None)
            state.set(MainAppStateProperties.ACTIVE_THREAD_CONVERSATION, None)

        # ----- Home Icon -----
        home_icon = ft.IconButton(
            icon=ft.Icons.HOME,
            icon_color=ft.Colors.SECONDARY,
            on_click=on_home_clicked,
            icon_size=30,
            style=ft.ButtonStyle(padding=0, bgcolor="transparent"),
        )

        # ----- Filter Menu -----
        def sort_by_date(_):
            nonlocal all_mails
            state.set(MainAppStateProperties.SORT_BY_DATE, True)
            mails = state.get(MainAppStateProperties.DISPLAYED_MAILS)
            if not all_mails and mails:
                all_mails = mails.copy()
            source = all_mails if all_mails else mails
            if not source:
                return
            sorted_mails = sorted(
                source,
                key=lambda c: max(
                    (t.last_message_datetime for t in c.threads),
                    default=datetime.datetime.min,
                ),
                reverse=True,
            )
            all_mails = sorted_mails.copy()
            state.set(MainAppStateProperties.DISPLAYED_MAILS, sorted_mails)

        def filter_unread(_):
            nonlocal all_mails
            state.set(MainAppStateProperties.SORT_BY_DATE, False)
            mails = state.get(MainAppStateProperties.DISPLAYED_MAILS)
            if not mails:
                return
            if not all_mails:
                all_mails = mails.copy()
            unread = [c for c in all_mails if any(t.unread_count > 0 for t in c.threads)]
            state.set(MainAppStateProperties.DISPLAYED_MAILS, unread)

        filter_menu = ft.PopupMenuButton(
            icon=ft.Icons.FILTER_LIST,
            tooltip="Filter / Sort",
            items=[
                ft.PopupMenuItem(
                    content=ft.Text("Sort by date"),
                    on_click=sort_by_date,
                ),
                ft.PopupMenuItem(
                    content=ft.Text("Show unread only"),
                    on_click=filter_unread,
                ),
            ],
        )

        def create_bottom_option(text: str, icon: ft.IconData, callback: Callable[[], None]):
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
            conversation = ConversationDTO(-1, contacts, [thread], False, None)
            state.set(MainAppStateProperties.ACTIVE_THREAD_CONVERSATION, conversation)
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
            try:
                bottom_row.update()
            except RuntimeError:
                pass

        state.listen_selection(None, on_selection_change)
        on_selection_change(None)

        # ----- Layout -----
        content = ft.Column(
            controls=[
                ft.Row([self.input, home_icon, filter_menu], alignment=ft.MainAxisAlignment.START),
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