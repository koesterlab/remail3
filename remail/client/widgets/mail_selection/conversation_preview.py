from collections.abc import Callable

import flet as ft
from flet.core.control_event import ControlEvent

from remail.client.widgets.mail_selection.profile_picture import create_profile_picture
from remail.controllers.dtos.conversations import ConversationDTO


class ConversationPreview(ft.Container):
    # component representing a single contact entry
    def __init__(
        self,
        conversation: ConversationDTO,
        primary_text: str,
        secondary_text: str,
        registered: bool,
        on_click: Callable[[], None],
    ):
        def toggle_fav(e:ControlEvent): #todo change in backend
            conversation.is_favorite = not conversation.is_favorite

        icon_btn = ft.Row([], spacing=2, expand=True, alignment=ft.MainAxisAlignment.END)

        if not registered:
            icon_btn.controls = [
                ft.IconButton(
                    icon=ft.Icons.ADD,
                    icon_color=ft.Colors.ON_SURFACE,
                    tooltip="Zu Kontakten hinzufügen",
                ),
                ft.IconButton(
                    icon=ft.Icons.DELETE, icon_color=ft.Colors.ON_SURFACE_VARIANT, tooltip="Spam"
                ),
            ]

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
            icon_btn.controls = [fav_button]

            def on_hover(e):
                fav_button.visible = conversation.is_favorite or e.data == "true"
                fav_button.update()

        super().__init__(
            on_hover=on_hover,
            on_click=lambda e: on_click(),
            bgcolor=ft.Colors.TRANSPARENT,
            margin=0,
            border=ft.border.only(bottom=ft.border.BorderSide(1, ft.Colors.GREY)),
            content=ft.Row(
                [
                    create_profile_picture(conversation),
                    ft.Column(
                        [
                            ft.Row(
                                [
                                    ft.Text(
                                        primary_text,
                                        weight=ft.FontWeight.BOLD,
                                        color=ft.Colors.ON_SURFACE,
                                    ),
                                ],
                                alignment=ft.MainAxisAlignment.START,
                            ),
                            ft.Row(
                                [
                                    ft.Text(
                                        secondary_text, size=12, color=ft.Colors.ON_SURFACE_VARIANT
                                    )
                                ],
                                alignment=ft.MainAxisAlignment.START,
                                spacing=6,
                            ),
                        ],
                        spacing=3,
                        alignment=ft.MainAxisAlignment.START,
                    ),
                    icon_btn,
                ],
                spacing=12,
                alignment=ft.MainAxisAlignment.START,
            ),
            padding=12,
        )
