"""Settings view with navigation and sub-views."""

import flet as ft

from remail.client.state import MainAppState, MainAppStateProperties
from remail.client.views.settings import (
    AppearanceView,
    AttachmentsView,
    EmailAccountsView,
    LanguageView,
    NotificationsView,
)
from remail.enums import SettingsSubView


class SettingsView(ft.Container):
    def __init__(self, state: MainAppState):
        super().__init__()
        back_button = ft.IconButton(
            icon=ft.Icons.ARROW_BACK,
            tooltip="Back to Dashboard",
            on_click=lambda: state.set(MainAppStateProperties.ACTIVE_SETTINGS, None),
        )

        # Create header with back button
        header = ft.Container(
            content=ft.Row(
                [
                    back_button,
                    ft.Text("Settings", size=24, weight=ft.FontWeight.BOLD),
                ],
            ),
            padding=ft.Padding.only(left=10, top=10, bottom=10),
        )

        # Create main layout
        sub_view = ft.Container(expand=True)
        main_row = ft.Row(
            controls=[
                ft.Container(
                    ft.Column(
                        controls=[
                            ft.TextButton(
                                content=label,
                                on_click=lambda _, v=link_name: state.set(
                                    MainAppStateProperties.ACTIVE_SETTINGS, v
                                ),
                                style=ft.ButtonStyle(
                                    color=ft.Colors.ON_SURFACE,
                                ),
                            )
                            for label, link_name in [
                                ("Appearance", SettingsSubView.APPEARANCE),
                                ("Attachments", SettingsSubView.ATTACHMENTS),
                                ("Email Accounts", SettingsSubView.EMAIL_ACCOUNTS),
                                ("Notification", SettingsSubView.NOTIFICATIONS),
                                ("Language", SettingsSubView.LANGUAGE),
                            ]
                        ],
                        spacing=16,
                    ),
                    width=200,
                    padding=10,
                ),
                ft.VerticalDivider(width=1),
                sub_view,
            ],
            expand=True,
        )

        def update_subview(view: SettingsSubView):
            if not view:
                return
            sub_view.content = {
                SettingsSubView.APPEARANCE: AppearanceView,
                SettingsSubView.ATTACHMENTS: AttachmentsView,
                SettingsSubView.EMAIL_ACCOUNTS: EmailAccountsView,
                SettingsSubView.LANGUAGE: LanguageView,
                SettingsSubView.NOTIFICATIONS: NotificationsView,
            }[view]()
            try:
                sub_view.update()
            except RuntimeError as _:
                pass

        update_subview(state.get(MainAppStateProperties.ACTIVE_SETTINGS))
        state.register_observer(MainAppStateProperties.ACTIVE_SETTINGS, update_subview)

        self.content = ft.Column(
            [
                header,
                ft.Divider(height=1),
                ft.Container(content=main_row, expand=True),
            ],
            expand=True,
        )
