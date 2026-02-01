import asyncio
from typing import cast

import flet as ft

from remail.client.state import AppState
from remail.client.views.dashboard_view import create_dashboard_view
from remail.client.widgets.chatbot.chatbot import create_chatbot
from remail.client.widgets.mail_selection import SelectionBar
from remail.controllers.account_controller import AccountController
from remail.controllers.dtos.conversations import ConversationDTO, ThreadPreviewDTO
from remail.controllers.dtos.user_dto import UserDTO
from remail.enums import MainView, SettingsSubView

from ...state.main_app_state import MainAppState, MainAppStateProperties
from ...widgets.thread.thread_list import ThreadList


def create_main_view(page: ft.Page, global_state: AppState):
    main_state = MainAppState()

    # State init
    main_state.set(MainAppStateProperties.DISPLAYED_MAILS, [])
    main_state.set(MainAppStateProperties.ACTIVE_CHATBOT, False)
    main_state.set(MainAppStateProperties.ACTIVE_THREAD, None)
    main_state.set(MainAppStateProperties.ACTIVE_CONVERSATION, [])
    main_state.set(MainAppStateProperties.SEARCH_TERM, "")

    selection_bar = SelectionBar(main_state)

    # ----------------------------
    # Navigation
    # ----------------------------
    def navigate_to_settings(p: SettingsSubView) -> None:
        if global_state.router:
            page.clean()
            global_state.settings_start_sub_view = p
            settings_view = global_state.router.load_view(MainView.SETTINGS)
            page.add(settings_view)
            page.update()

    main_state.navigate_to_settings = navigate_to_settings

    settings_button = ft.IconButton(
        icon=ft.Icons.SETTINGS,
        tooltip="Settings",
        on_click=lambda _: navigate_to_settings(SettingsSubView.EMAIL_ACCOUNTS),
    )

    # ----------------------------
    # Views (right side)
    # ----------------------------
    empty_accounts_view = ft.Container(
        ft.Column(
            [
                ft.Text("No email accounts connected yet", size=18, weight=ft.FontWeight.BOLD),
                ft.Text("Add an account in Settings to start syncing your inbox."),
                ft.ElevatedButton(
                    "Open Settings",
                    icon=ft.Icons.SETTINGS,
                    on_click=lambda _: navigate_to_settings(SettingsSubView.EMAIL_ACCOUNTS),
                ),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=12,
            expand=True,
        ),
        padding=20,
        expand=True,
    )

    # Placeholder dashboard until we know active user id
    dashboard_placeholder = ft.Column(
        [
            ft.Container(
                content=ft.Row([settings_button], alignment=ft.MainAxisAlignment.END),
                padding=10,
            ),
            ft.Container(expand=True),
        ],
        expand=True,
    )

    right_view = ft.Container(
        content=dashboard_placeholder,
        col={"xs": 6, "md": 8, "lg": 9},
        expand=True,
    )

    # ----------------------------
    # Chatbot + layout
    # ----------------------------
    chatbot = create_chatbot(main_state)
    chatbot.height = 60
    chatbot.expand = False

    container = ft.ResponsiveRow(
        expand=True,
        controls=[
            ft.Column(
                [ft.Container(selection_bar, expand=1), chatbot],
                col={"xs": 6, "md": 4, "lg": 3},
            ),
            right_view,
        ],
    )

    # ----------------------------
    # Observers
    # ----------------------------
    def _active_user_id() -> int | None:
        u = cast(UserDTO | None, main_state.get(MainAppStateProperties.ACTIVE_USER))
        if u is None:
            return None
        return u.id

    def on_thread_change(new: ThreadPreviewDTO | None) -> None:
        if new:
            right_view.content = ThreadList(main_state)
        else:
            uid = _active_user_id()
            right_view.content = (
                create_dashboard_view(page, global_state, uid)
                if uid is not None
                else empty_accounts_view
            )
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

    # ----------------------------
    # Sync callbacks
    # ----------------------------
    def on_emails_synced(acting_account: UserDTO, updates: list[ConversationDTO]) -> None:
        active = cast(UserDTO | None, main_state.get(MainAppStateProperties.ACTIVE_USER))
        if active is not None and acting_account.id == active.id:
            conversations: list[ConversationDTO] = main_state.get(
                MainAppStateProperties.DISPLAYED_MAILS
            )
            for update in updates:
                for i in range(len(conversations)):
                    if conversations[i].id == update.id:
                        conversations[i] = update
                        break
                else:
                    conversations.append(update)
            main_state.trigger(MainAppStateProperties.DISPLAYED_MAILS)

    def on_email_sync_error(acting_account: UserDTO, msg: str) -> None:
        snack_bar = ft.SnackBar(
            ft.Text(
                f"[{acting_account.username}] Error while syncing mails: {msg}",
                color=ft.Colors.ON_ERROR,
            ),
            bgcolor=ft.Colors.ERROR,
            duration=50_000,
        )
        page.overlay.append(snack_bar)
        snack_bar.open = True
        page.update()

    # stop old listeners
    for t in main_state.sync_threads:
        t.cancel()

    # register new accounts and start listening
    accounts = AccountController.all_client_accounts()

    if not accounts:
        main_state.set(MainAppStateProperties.ACTIVE_USER, None)
        right_view.content = empty_accounts_view
        right_view.update()
    else:
        for acc in accounts:
            main_state.account_controllers[acc.get_email_address()] = acc
            acc.set_callback_email_changes(
                lambda updates, acc_=acc: on_emails_synced(acc_.get_user(), updates)
            )
            acc.set_callback_email_errors(
                lambda msg, acc_=acc: on_email_sync_error(acc_.get_user(), msg)
            )

            page.run_thread(lambda acc_=acc: asyncio.run(acc_.start_listening()))

        main_state.set(MainAppStateProperties.ACTIVE_USER, accounts[0].get_user())

        uid = _active_user_id()
        right_view.content = (
            create_dashboard_view(page, global_state, uid)
            if uid is not None
            else empty_accounts_view
        )
        right_view.update()

    return container
