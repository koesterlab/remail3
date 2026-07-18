import asyncio
import logging
from typing import cast

import flet as ft

from remail.client.views.settings.attachments_view import AttachmentsView
from remail.client.widgets.chatbot.chatbot import create_chatbot
from remail.client.widgets.mail_selection import SelectionBar
from remail.controllers.account_controller import AccountController
from remail.controllers.dtos.conversations import ConversationDTO, ThreadPreviewDTO
from remail.controllers.dtos.user_dto import UserDTO
from remail.enums import SettingsSubView

from ...state.main_app_state import MainAppState, MainAppStateProperties
from ...widgets.dashboard.dashboard_page import DashboardPage
from ...widgets.thread.thread_list import ThreadList

_logger = logging.getLogger(__name__)


class EmailView(ft.Container):
    def __init__(self, state: MainAppState) -> None:
        super().__init__()

        def on_thread_change(new: ThreadPreviewDTO | None) -> None:
            if new and state.get(MainAppStateProperties.ACTIVE_ATTACHMENTS):
                state.set(MainAppStateProperties.ACTIVE_ATTACHMENTS, False)
                return
            update_right_view()

        def on_attachments_change(_: bool) -> None:
            update_right_view()

        def update_right_view() -> None:
            active_thread = state.get(MainAppStateProperties.ACTIVE_THREAD)
            if active_thread:
                right_view.content = ThreadList(state)
            elif state.get(MainAppStateProperties.ACTIVE_ATTACHMENTS):
                right_view.content = AttachmentsView()
            else:
                dashboard_page.refresh()  # pick up background changes (e.g. auto-tagging)
                right_view.content = dashboard
            try:
                right_view.update()
            except RuntimeError:
                pass

        def on_active_user_change(user: UserDTO):
            if user is None:
                return
            controller = state.account_controllers.get(user.email)
            if controller is None:
                return
            dashboard_page.refresh()  # pick up background changes (e.g. auto-tagging)
            right_view.content = dashboard
            right_view.update()
            state.set(MainAppStateProperties.DISPLAYED_MAILS, [])
            on_emails_synced(user, list(controller._get_conversations_from_db()))

        def on_emails_synced(acting_account: UserDTO, updates: list[ConversationDTO]):
            if acting_account == state.get(
                MainAppStateProperties.ACTIVE_USER
            ):  # if active account: show new mails
                # todo: more efficient resync (maybe with observable conversation DTOs)
                conversations: list[ConversationDTO] = state.get(
                    MainAppStateProperties.DISPLAYED_MAILS
                )
                for update in updates:
                    for i in range(len(conversations)):
                        if conversations[i].id == update.id:
                            conversations[i] = update
                            break
                    else:  # conversation was not found in last state
                        conversations.append(update)
                state.trigger(
                    MainAppStateProperties.DISPLAYED_MAILS
                )  # object (array) stays the same, no need to set it again
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
            self.page.overlay.append(snack_bar)
            snack_bar.open = True
            self.page.update()

        # stop old listeners
        for t in state.sync_threads:
            t.cancel()

        self.accounts: list[AccountController] = []
        self._state = state
        self._on_emails_synced = on_emails_synced
        self._on_email_sync_error = on_email_sync_error
        state.set(MainAppStateProperties.ACTIVE_USER, None)

        def on_accounts_changed(_email: str | None) -> None:
            new_accounts = AccountController.all_client_accounts()
            current_emails = {acc.get_email_address() for acc in new_accounts}
            for email in list(state.account_controllers.keys()):
                if email not in current_emails:
                    state.account_controllers.pop(email, None)
            self.accounts = [a for a in self.accounts if a.get_email_address() in current_emails]
            print(self.accounts)



            for acc in new_accounts:
                if acc.get_email_address() not in state.account_controllers:
                    state.account_controllers[acc.get_email_address()] = acc
                    acc.set_callback_email_changes(
                        lambda updates, acc_=acc: on_emails_synced(acc_.get_user(), updates) # type: ignore[misc]
                    )
                    acc.set_callback_email_errors(
                        lambda msg, acc_=acc: on_email_sync_error(acc_.get_user(), msg) # type: ignore[misc]
                    )
                    self.accounts.append(acc)
                    cast(ft.Page, self.page).run_thread(
                        lambda acc_=acc: asyncio.run(acc_.start_listening()) # type: ignore[misc]
                    )
                else:
                    state.account_controllers[acc.get_email_address()].user = acc.get_user()

            active_user = state.get(MainAppStateProperties.ACTIVE_USER)
            if not new_accounts:
                state.set(MainAppStateProperties.ACTIVE_USER, None)
            elif not active_user or active_user.email not in current_emails:
                state.set(MainAppStateProperties.ACTIVE_USER, new_accounts[0].get_user())
            else:
                state.trigger(MainAppStateProperties.ACTIVE_USER)

        state.register_observer(MainAppStateProperties.ACTIVE_THREAD, on_thread_change)
        state.register_observer(MainAppStateProperties.ACTIVE_ATTACHMENTS, on_attachments_change)
        state.register_observer(MainAppStateProperties.ACTIVE_USER, on_active_user_change)
        state.register_observer(MainAppStateProperties.ACCOUNTS_CHANGED, on_accounts_changed)

        empty_accounts_view = ft.Container(
            ft.Column(
                [
                    ft.Text("No email accounts connected yet", size=18, weight=ft.FontWeight.BOLD),
                    ft.Text("Add an account in Settings to start syncing your inbox."),
                    ft.Button(
                        "Open Settings",
                        icon=ft.Icons.SETTINGS,
                        on_click=lambda _: state.set(
                            MainAppStateProperties.ACTIVE_SETTINGS, SettingsSubView.EMAIL_ACCOUNTS
                        ),
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

        dashboard_page = DashboardPage(state)
        dashboard = ft.Container(content=dashboard_page, padding=10)

        right_view = ft.Container(
            dashboard if state.account_controllers else empty_accounts_view,
            col={"xs": 6, "md": 8, "lg": 9},
            expand=True,
        )

        chatbot = create_chatbot(state)

        self.content = ft.ResponsiveRow(
            expand=True,
            controls=[
                ft.Container(
                    content=ft.Column(
                        [
                            ft.Container(SelectionBar(state), expand=1),
                            ft.Container(chatbot),
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        expand=True,
                    ),
                    col={"xs": 6, "md": 4, "lg": 3},
                    expand=True,
                ),
                right_view,
            ],
        )

    def run_sync_threads(self):
        cast(ft.Page, self.page).run_thread(self._init_accounts)

    def _init_accounts(self):
        from remail.utils.timer import Timer

        page = cast(ft.Page, self.page)
        _logger.info("Loading accounts...")
        t = Timer()
        accounts = AccountController.all_client_accounts()
        _logger.info("Accounts loaded: %d account(s). (%s)", len(accounts), t.elapsed())
        if accounts:
            self.accounts = accounts
            for acc in accounts:
                self._state.account_controllers[acc.get_email_address()] = acc
                acc.set_callback_email_changes(
                    lambda updates, acc_=acc: self._on_emails_synced(acc_.get_user(), updates)  # type:ignore
                )
                acc.set_callback_email_errors(
                    lambda msg, acc_=acc: self._on_email_sync_error(acc_.get_user(), msg)  # type:ignore
                )
            _logger.info("Setting ACTIVE_USER, triggering observers...")
            t2 = Timer()
            self._state.set(MainAppStateProperties.ACTIVE_USER, accounts[0].get_user())
            _logger.info("Observers done. (%s)", t2.elapsed())
        _logger.info("Scheduling sync threads...")
        for acc in self.accounts:
            page.run_thread(
                lambda acc_=acc: asyncio.run(acc_.start_listening())  # type: ignore[misc]
            )
        _logger.info("_init_accounts done. Total: (%s)", t.elapsed())
