import asyncio

import flet as ft

from remail.client.state import AppState
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
    main_state.set(MainAppStateProperties.DISPLAYED_MAILS, [])
    main_state.set(MainAppStateProperties.ACTIVE_CHATBOT, False)
    main_state.set(MainAppStateProperties.ACTIVE_THREAD, None)
    main_state.set(MainAppStateProperties.ACTIVE_CONVERSATION, [])
    main_state.set(MainAppStateProperties.SEARCH_TERM, "")
    selection_bar = SelectionBar(main_state)

    # Settings button
    def navigate_to_settings(e):
        """Navigate to settings page."""
        if global_state.router:
            global_state.settings_start_sub_view = SettingsSubView.EMAIL_ACCOUNTS
            page.clean()
            settings_view = global_state.router.load_view(MainView.SETTINGS)
            page.add(settings_view)
            page.update()

    settings_button = ft.IconButton(
        icon=ft.Icons.SETTINGS,
        tooltip="Settings",
        on_click=navigate_to_settings,
    )

    dashboard_header = ft.Container(
        content=ft.Row(
            [
                ft.Text("Dashboard (vertrau ist fast fertig)", size=20),
                settings_button,
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        ),
        padding=10,
    )

    dashboard = ft.Column([dashboard_header], expand=True)

    empty_accounts_view = ft.Container(
        ft.Column(
            [
                ft.Text("No email accounts connected yet", size=18, weight=ft.FontWeight.BOLD),
                ft.Text("Add an account in Settings to start syncing your inbox."),
                ft.ElevatedButton(
                    "Open Settings",
                    icon=ft.Icons.SETTINGS,
                    on_click=navigate_to_settings,
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
    right_view = ft.Container(
        dashboard, col={"xs": 6, "md": 8, "lg": 9}, expand=True, bgcolor=ft.Colors.RED
    )

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

    def on_thread_change(new: ThreadPreviewDTO | None) -> None:
        if new:
            right_view.content = ThreadList(main_state)
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

    def on_emails_synced(acting_account: UserDTO, updates: list[ConversationDTO]):
        if acting_account == main_state.get(
            MainAppStateProperties.ACTIVE_USER
        ):  # if active account: show new mails
            # todo: more efficient resync (maybe with observable conversation DTOs)
            conversations: list[ConversationDTO] = main_state.get(
                MainAppStateProperties.DISPLAYED_MAILS
            )
            for update in updates:
                for i in range(len(conversations)):
                    if conversations[i].id == update.id:
                        conversations[i] = update
                        break
                else:  # conversation was not found in last state
                    conversations.append(update)
            main_state.trigger(
                MainAppStateProperties.DISPLAYED_MAILS
            )  # object (array) stays the same, no need to set it again
            print(conversations)
        else:
            pass  # todo: set "news available on this account"-hint

    def on_email_sync_error(acting_account: UserDTO, msg: str):
        snack_bar = ft.SnackBar(
            ft.Text(
                "[" + acting_account.email + "] Error while syncing mails: " + msg,
                color=ft.Colors.ON_ERROR,
            ),
            bgcolor=ft.Colors.ERROR,
            duration=50000,
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
        dashboard.controls.append(empty_accounts_view)
        right_view.content = dashboard
        main_state.set(MainAppStateProperties.ACTIVE_USER, None)
    else:
        for acc in accounts:
            main_state.account_controllers[acc.get_email_address()] = acc
            acc.set_callback_email_changes(
                lambda updates, acc_=acc: on_emails_synced(acc_.get_user(), updates)
            )
            acc.set_callback_email_errors(
                lambda msg, acc_=acc: on_email_sync_error(acc_.get_user(), msg)
            )

            page.run_thread(
                lambda acc_=acc: asyncio.run(acc_.start_listening())
            )  # running sync task in flets own async system

        main_state.set(MainAppStateProperties.ACTIVE_USER, accounts[0].get_user())
    main_state.register_observer(MainAppStateProperties.ACTIVE_CHATBOT, on_chatbot_state_change)
    main_state.register_observer(MainAppStateProperties.ACTIVE_THREAD, on_thread_change)

    return container
