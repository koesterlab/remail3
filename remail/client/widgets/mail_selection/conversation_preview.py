from abc import ABC
from collections.abc import Callable

import flet as ft
from flet.core.circle_avatar import CircleAvatar
from flet.core.control_event import ControlEvent

from remail.client.state import MainAppState, MainAppStateProperties
from remail.client.widgets.mail_selection.profile_picture import create_profile_picture
from remail.controllers.dtos.conversations import ConversationDTO


class ConversationPreview(ft.Container, ABC):
    # component representing a single contact entry
    def __init__(
        self,
        state: MainAppState,
        conversation: ConversationDTO,
        primary_text: str,
        secondary_text: str,
        registered: bool,
        on_click: Callable[[], None],
    ):
        def toggle_fav(e: ControlEvent):  # todo change in backend
            conversation.is_favorite = not conversation.is_favorite
            fav_button.icon = ft.Icons.STAR if conversation.is_favorite else ft.Icons.STAR_OUTLINE
            state.trigger(MainAppStateProperties.DISPLAYED_MAILS)  # reload to reorder
            if fav_button.page:
                fav_button.update()

        if not registered:
            icon_btn = ft.Column(
                [
                    ft.IconButton(
                        icon=ft.Icons.ADD,
                        icon_color=ft.Colors.ON_SURFACE,
                        tooltip="Add to Contacts",
                        # sizing
                        icon_size=20,
                        size_constraints=ft.BoxConstraints(max_width=20, max_height=20),
                        padding=0,
                        splash_radius=20,
                    ),
                    ft.IconButton(
                        icon=ft.Icons.DELETE,
                        icon_color=ft.Colors.ON_SURFACE_VARIANT,
                        tooltip="Delete Chats",
                        # sizing
                        icon_size=20,
                        size_constraints=ft.BoxConstraints(max_width=20, max_height=20),
                        padding=0,
                        splash_radius=20,
                    ),
                ],
                spacing=1,
                alignment=ft.MainAxisAlignment.CENTER,
            )

            def on_hover(e):
                pass
        else:
            fav_button = ft.IconButton(
                icon=ft.Icons.STAR if conversation.is_favorite else ft.Icons.STAR_OUTLINE,
                tooltip="Favorit",
                on_click=toggle_fav,
                icon_color=ft.Colors.ON_SURFACE_VARIANT,
                visible=conversation.is_favorite,
            )
            icon_btn = ft.Row(
                [fav_button],
                alignment=ft.MainAxisAlignment.END,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            )

            def on_hover(e):
                fav_button.visible = conversation.is_favorite or e.data == "true"
                fav_button.update()

        profile_picture = ft.Container()
        profile_picture.on_click = lambda e: state.toggle_selection(conversation)

        def on_toggle_selection(is_selected: bool):
            if is_selected:
                profile_picture.content = CircleAvatar(
                    ft.Icon(ft.Icons.CHECK, color=ft.Colors.BLUE_900), bgcolor=ft.Colors.BLUE_200
                )
            else:
                profile_picture.content = create_profile_picture(conversation)
            if profile_picture.page:
                profile_picture.update()

        state.listen_selection(conversation, on_toggle_selection)
        on_toggle_selection(conversation in state.get_selected())

        super().__init__(
            on_hover=on_hover,
            on_click=lambda e: on_click(),
            bgcolor=ft.Colors.TRANSPARENT,
            margin=0,
            border=ft.border.only(bottom=ft.border.BorderSide(1, ft.Colors.GREY)),
            content=ft.Row(
                [
                    profile_picture,
                    ft.Column(
                        [
                            ft.Row(
                                [
                                    ft.Text(
                                        primary_text,
                                        weight=ft.FontWeight.BOLD,
                                        color=ft.Colors.ON_SURFACE,
                                        expand=True,
                                        overflow=ft.TextOverflow.ELLIPSIS,
                                        max_lines=2,
                                    ),
                                ],
                                alignment=ft.MainAxisAlignment.START,
                            ),
                            ft.Row(
                                [
                                    ft.Text(
                                        secondary_text,
                                        size=12,
                                        color=ft.Colors.ON_SURFACE_VARIANT,
                                        expand=True,
                                        overflow=ft.TextOverflow.ELLIPSIS,
                                        max_lines=1,
                                    )
                                ],
                                alignment=ft.MainAxisAlignment.START,
                                spacing=6,
                            ),
                        ],
                        spacing=3,
                        alignment=ft.MainAxisAlignment.START,
                        expand=True,
                    ),
                    icon_btn,
                ],
                spacing=12,
                alignment=ft.MainAxisAlignment.START,
            ),
            padding=12,
        )
