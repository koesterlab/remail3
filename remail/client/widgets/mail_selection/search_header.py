import flet as ft
from flet.core.control_event import ControlEvent

from remail.client.state.main_app_state import MainAppState, MainAppStateProperties


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
            # todo: load mails from controller

        # ----- Home Icon -----
        home_icon = ft.IconButton(
            icon=ft.Icons.HOME,
            icon_color=ft.Colors.SECONDARY,
            on_click=on_home_clicked,
            icon_size=30,
            style=ft.ButtonStyle(padding=0, bgcolor="transparent"),
        )

        # ----- Links unterhalb -----
        archiv_link = ft.Container(
            ft.Text(
                "Archiv",
                style=ft.TextStyle(decoration=ft.TextDecoration.UNDERLINE),
                color=ft.Colors.TERTIARY,
            ),
            # todo: load mails from controller into state on_click=lambda _: ,
        )

        spam_link = ft.Container(
            content=ft.Text(
                "Spam",
                style=ft.TextStyle(decoration=ft.TextDecoration.UNDERLINE),
                color=ft.Colors.TERTIARY,
            ),
            # todo: same as above on_click=lambda _: ,
        )

        # ----- Layout -----
        content = ft.Column(
            controls=[
                ft.Row([self.input, home_icon], alignment=ft.MainAxisAlignment.START),
                ft.Row([archiv_link, spam_link], spacing=20),
                ft.Divider(height=3, thickness=2),
            ],
            spacing=5,
        )

        super().__init__(
            content=content,
            padding=2,
            margin=1,
        )
