from __future__ import annotations

import asyncio
import importlib
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from types import SimpleNamespace
from unittest.mock import Mock

import flet as ft
import pytest

from remail.client.index import main, show_snack_bar, update_page
from remail.client.state.main_app_state import MainAppState, MainAppStateProperties
from remail.client.views.index_view import IndexView
from remail.client.views.settings.settings_sub_view import SettingsSubView
from remail.client.views.settings.settings_view import SettingsView
from remail.client.widgets.dashboard.account_card import AccountCard
from remail.client.widgets.dashboard.appointment_item import AppointmentItem
from remail.client.widgets.dashboard.appointments_list import AppointmentsList
from remail.client.widgets.dashboard.croppable_email_adress import (
    create_croppable_email_address,
)
from remail.client.widgets.dashboard.dashboard_page import (
    DashboardPage,
    _display_name_from_account,
    _time_greeting,
)
from remail.client.widgets.dashboard.todo_item import TodoItem, _preview_tags
from remail.client.widgets.dashboard.todo_list import TodoList
from remail.client.widgets.mail_selection.contact_preview import ContactPreview
from remail.client.widgets.mail_selection.conversation_preview import ConversationPreview
from remail.client.widgets.mail_selection.conversation_selection import ConversationSelection
from remail.client.widgets.mail_selection.group_preview import GroupPreview
from remail.client.widgets.mail_selection.profile_picture import (
    create_contact_picture,
    create_profile_picture,
)
from remail.client.widgets.mail_selection.search_header import SearchHeader
from remail.client.widgets.mail_selection.selection_bar import SelectionBar
from remail.client.widgets.mail_selection.thread_selection import ThreadSelection
from remail.client.widgets.thread.message_bubble import MessageBubble
from remail.client.widgets.thread.new_message_dialog import create_new_message_dialog
from remail.controllers.dtos.conversations import ContactDTO, ConversationDTO, ThreadPreviewDTO
from remail.controllers.dtos.settings_dto import SettingsDTO
from remail.controllers.dtos.threads import MessageContentDTO, MessageDTO, SenderDTO, ThreadDTO
from remail.controllers.dtos.user_dto import UserDTO
from remail.enums import (
    ContactType,
    FontFamily,
    FontSize,
    Language,
    Protocol,
    ThemeMode,
    Timezone,
    UserAccountCategory,
)
from remail.enums import (
    SettingsSubView as SettingsSubViewEnum,
)


@dataclass
class StubAppState:
    theme_mode: ThemeMode = ThemeMode.SYSTEM
    font_size: FontSize = FontSize.MEDIUM
    font_family: FontFamily = FontFamily.ARIAL
    language: Language = Language.ENGLISH
    timezone: Timezone = Timezone.EUROPE_BERLIN
    desktop_notifications: bool = True
    email_notifications: bool = True
    quiet_hours: bool = False
    connected_emails: list[object] = field(default_factory=list)


def make_user(user_id: int = 1, email: str = "user@example.com", unread: int = 0) -> UserDTO:
    return UserDTO(
        id=user_id,
        name="User Example",
        email=email,
        category=UserAccountCategory.PRIVATE,
        protocol=Protocol.IMAP,
        unread_conversations=unread,
    )


def make_contact(contact_id: int = 1, email: str = "contact@example.com") -> ContactDTO:
    return ContactDTO(
        id=contact_id,
        first_name="Ada",
        last_name="Lovelace",
        email=email,
        is_known=True,
        type=ContactType.PRIVATE,
    )


def make_thread_preview(thread_id: int = 1, title: str = "Subject") -> ThreadPreviewDTO:
    return ThreadPreviewDTO(
        thread_id=thread_id,
        title=title,
        total_count=1,
        unread_count=1,
        last_message="Hello",
        last_message_datetime=datetime.now(),
    )


def make_conversation(
    conv_id: int = 1, contacts: list[ContactDTO] | None = None
) -> ConversationDTO:
    return ConversationDTO(
        id=conv_id,
        contacts=contacts or [make_contact(conv_id)],
        threads=[make_thread_preview(conv_id)],
        is_favorite=False,
        custom_name=None,
    )


def make_message() -> MessageDTO:
    sender = SenderDTO(id=1, first_name="Ada", last_name="Lovelace", email="ada@example.com")
    return MessageDTO(
        id=1,
        sender=sender,
        subject="Subject",
        content=MessageContentDTO(body="Hello world", attachments=[]),
        sent_at=datetime.now() - timedelta(hours=2),
    )


@pytest.fixture(autouse=True)
def patch_control_updates(monkeypatch):
    monkeypatch.setattr(ft.Control, "update", lambda self: None, raising=False)


def test_client_entry_points_render_and_update(monkeypatch):
    fake_view = Mock(spec=IndexView)
    fake_page = Mock(spec=ft.Page)

    monkeypatch.setattr("remail.client.index.IndexView", lambda: fake_view)

    main(fake_page)
    show_snack_bar(ft.Text("ok"))
    update_page()

    assert fake_page.add.called
    assert fake_view.start.called
    assert fake_page.update.called
    assert fake_page.show_dialog.called


def test_index_view_start_smoke(monkeypatch):
    created_states: list[MainAppState] = []

    class FakeSettingsView(ft.Container):
        def __init__(self, state):
            created_states.append(state)
            super().__init__()

    class FakeEmailView(ft.Container):
        def __init__(self, state):
            created_states.append(state)
            super().__init__()

        def run_sync_threads(self):
            self.ran = True

    monkeypatch.setattr("remail.client.views.index_view.SettingsView", FakeSettingsView)
    monkeypatch.setattr("remail.client.views.index_view.EmailView", FakeEmailView)

    view = IndexView()
    view.start()

    assert isinstance(view, ft.Container)
    assert created_states


def test_email_view_smoke(monkeypatch):
    state = MainAppState()
    account_user = make_user()
    fake_account = Mock()
    fake_account.get_email_address.return_value = account_user.email
    fake_account.get_user.return_value = account_user
    fake_account.set_callback_email_changes.return_value = None
    fake_account.set_callback_email_errors.return_value = None
    fake_account.start_listening = Mock()

    monkeypatch.setattr(
        "remail.client.views.main.email_view.create_chatbot", lambda state: ft.Container()
    )
    monkeypatch.setattr(
        "remail.client.views.main.email_view.SelectionBar", lambda state: ft.Container()
    )
    monkeypatch.setattr(
        "remail.client.views.main.email_view.DashboardPage", lambda state: ft.Container()
    )
    monkeypatch.setattr(
        "remail.client.views.main.email_view.ThreadList", lambda state: ft.Container()
    )
    monkeypatch.setattr(
        "remail.client.views.main.email_view.AccountController.all_client_accounts",
        lambda: [fake_account],
    )

    from remail.client.views.main.email_view import EmailView

    view = EmailView(state)
    state.set(MainAppStateProperties.ACTIVE_THREAD, make_thread_preview())
    state.set(MainAppStateProperties.ACTIVE_CHATBOT, True)

    assert isinstance(view, ft.Container)


def test_settings_views_and_subview_apply(monkeypatch):
    dto = SettingsDTO(
        id=1,
        theme_mode=ThemeMode.SYSTEM,
        font_size=FontSize.MEDIUM,
        font_family=FontFamily.ARIAL,
        language=Language.ENGLISH,
        timezone=Timezone.EUROPE_BERLIN,
        desktop_notifications=True,
        email_notifications=True,
        quiet_hours=False,
        llm_url="http://llm",
        llm_key="key",
    )
    controller = Mock()
    controller.get_settings.return_value = dto
    controller.update_settings.return_value = None
    monkeypatch.setattr(
        "remail.client.views.settings.settings_sub_view.SettingsController", lambda: controller
    )

    class DemoSubview(SettingsSubView):
        def create_page(self, settings):
            return ft.Container()

    subview = DemoSubview()
    subview.apply_settings("language", Language.GERMAN)

    monkeypatch.setattr(
        "remail.client.views.settings.email_accounts_view.AccountController.all_client_accounts",
        lambda: [],
    )
    monkeypatch.setattr(
        "remail.client.views.settings.settings_view.AppearanceView", lambda: ft.Container()
    )
    monkeypatch.setattr(
        "remail.client.views.settings.settings_view.EmailAccountsView", lambda: ft.Container()
    )
    monkeypatch.setattr(
        "remail.client.views.settings.settings_view.LanguageView", lambda: ft.Container()
    )
    monkeypatch.setattr(
        "remail.client.views.settings.settings_view.NotificationsView", lambda: ft.Container()
    )

    appearance = importlib.import_module(
        "remail.client.views.settings.appearance_view"
    ).AppearanceView()
    language = importlib.import_module("remail.client.views.settings.language_view").LanguageView()
    notifications = importlib.import_module(
        "remail.client.views.settings.notifications_view"
    ).NotificationsView()
    email_accounts = importlib.import_module(
        "remail.client.views.settings.email_accounts_view"
    ).EmailAccountsView()

    state = MainAppState()
    state.set(MainAppStateProperties.ACTIVE_SETTINGS, SettingsSubViewEnum.APPEARANCE)
    settings_view = SettingsView(state)
    state.set(MainAppStateProperties.ACTIVE_SETTINGS, SettingsSubViewEnum.NOTIFICATIONS)

    assert isinstance(appearance, ft.Container)
    assert isinstance(language, ft.Container)
    assert isinstance(notifications, ft.Container)
    assert isinstance(email_accounts, ft.Container)
    assert isinstance(settings_view, ft.Container)


def test_dashboard_widgets_smoke(monkeypatch):
    state = MainAppState()
    user = make_user(unread=3)
    state.set(MainAppStateProperties.ACTIVE_USER, user)
    state.account_controllers[user.email] = Mock(
        get_user=Mock(return_value=user),
        user_id=user.id,
        id=user.id,
        name=user.name,
        email=user.email,
    )
    state.thread_controller.get_most_urgent_threads = Mock(
        return_value=[
            (ThreadDTO(id=1, title="Todo", messages=[make_message()]), make_conversation(), user)
        ]
    )
    monkeypatch.setattr(
        "remail.client.widgets.dashboard.appointments_list.DashboardService.get_recent_appointment_items_for_user",
        lambda user_id: [(make_thread_preview(), datetime.now())],
    )

    page = DashboardPage(state)
    page.on_user_change(user)
    state.set(MainAppStateProperties.ACTIVE_USER, user)

    assert _time_greeting(datetime(2026, 1, 1, 9)) == "Good morning"
    assert _display_name_from_account({"email": "ada.lovelace@example.com"}) == "Ada Lovelace"
    assert isinstance(AccountCard(user), ft.Container)
    assert isinstance(AppointmentItem(make_thread_preview(), datetime.now(), user), ft.Container)
    assert isinstance(AppointmentsList(state), ft.Container)
    assert isinstance(
        create_croppable_email_address("a@example.com", 12, ft.Colors.BLACK), ft.Container
    )
    assert isinstance(
        create_croppable_email_address("invalid-email", 12, ft.Colors.BLACK), ft.Container
    )
    assert isinstance(
        TodoItem(state, ThreadDTO(id=1, title="Todo", messages=[make_message()]), user),
        ft.Container,
    )
    assert TodoItem.fmt_badge(datetime.now() - timedelta(days=1)) == "yesterday"
    assert isinstance(TodoList(state), ft.Container)
    assert isinstance(page, ft.Column)


def test_todo_preview_tags_and_visible_count():
    state = MainAppState()
    user = make_user()
    empty_thread = ThreadDTO(id=1, title="Empty", messages=[])
    work_thread = ThreadDTO(
        id=2,
        title="Project update",
        messages=[make_message()],
    )
    newsletter_thread = ThreadDTO(
        id=3,
        title="Newsletter invoice",
        messages=[make_message()],
    )
    state.thread_controller.get_most_urgent_threads = Mock(
        return_value=[
            (empty_thread, make_conversation(), user),
            (work_thread, make_conversation(), user),
            (newsletter_thread, make_conversation(), user),
        ]
    )

    todo_list = TodoList(state)
    content_column = todo_list.content
    header_row = content_column.controls[0]
    header_column = header_row.controls[0]
    items_column = content_column.controls[1]

    assert header_column.controls[1].value == "2 emails to answer"
    assert len(items_column.controls) == 2
    assert _preview_tags(
        "Newsletter",
        "Your invoice is ready",
        datetime.now() - timedelta(days=4),
    ) == ["Newsletter", "Finance"]

    todo_list._set_filter("Newsletter")

    assert todo_list.count_text.value == "1 email to answer"
    assert len(todo_list.items_column.controls) == 1

    todo_list._set_filter("Urgent")

    assert todo_list.count_text.value == "0 emails to answer"
    assert todo_list.items_column.controls[0].value == "No emails match this tag"


def test_mail_selection_and_thread_widgets_smoke(monkeypatch):
    state = MainAppState()
    conversation = make_conversation()
    state.set(MainAppStateProperties.DISPLAYED_MAILS, [conversation])
    state.account_controllers["user@example.com"] = Mock(search=Mock(return_value=[conversation]))
    state.set(MainAppStateProperties.ACTIVE_USER, make_user())

    fake_page = SimpleNamespace(run_task=lambda fn: asyncio.run(fn()))
    monkeypatch.setattr(ConversationSelection, "page", property(lambda self: fake_page))

    conversation_selection = ConversationSelection(state)
    thread_selection = ThreadSelection(state)
    selection_bar = SelectionBar(state)
    search_header = SearchHeader(state)
    thread_selection.set_content(conversation)
    state.set(MainAppStateProperties.SEARCH_TERM, "contact")
    state.set(MainAppStateProperties.ACTIVE_CONVERSATION, conversation)

    assert isinstance(ContactPreview(state, conversation), ConversationPreview)
    assert isinstance(
        GroupPreview(
            state, make_conversation(2, [make_contact(2), make_contact(3, "b@example.com")])
        ),
        ConversationPreview,
    )
    assert isinstance(create_profile_picture(conversation), ft.CircleAvatar)
    assert isinstance(create_contact_picture(make_contact()), ft.CircleAvatar)
    assert isinstance(conversation_selection, ft.Container)
    assert isinstance(search_header, ft.Container)
    assert isinstance(selection_bar, ft.Container)
    assert isinstance(thread_selection, ft.Container)


def test_message_bubble_and_new_message_dialog_smoke():
    state = MainAppState()
    state.thread_controller = Mock()
    state.thread_controller.create_thread.return_value = make_thread_preview(99, "Created")
    state.thread_controller.send_message.return_value = None
    current_user = make_contact()
    other_sender = SenderDTO(
        id=2, first_name="Grace", last_name="Hopper", email="grace@example.com"
    )
    message = MessageDTO(
        id=1,
        sender=other_sender,
        subject="Subject",
        content=MessageContentDTO(body="Hi", attachments=[]),
        sent_at=datetime.now(),
    )

    dialog = create_new_message_dialog(state)
    state.set(MainAppStateProperties.DRAFT, "Hello")
    state.set(MainAppStateProperties.ACTIVE_THREAD, make_thread_preview(-1, "New Topic"))
    state.set(
        MainAppStateProperties.ACTIVE_THREAD_CONVERSATION,
        ConversationDTO(
            id=-1,
            contacts=[make_contact()],
            threads=[make_thread_preview(-1, "New Topic")],
            is_favorite=False,
            custom_name=None,
        ),
    )

    assert isinstance(MessageBubble(message, current_user), ft.Container)
    assert isinstance(dialog, ft.Container)
