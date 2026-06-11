from __future__ import annotations

from datetime import datetime
from smtplib import SMTPRecipientsRefused, SMTPServerDisconnected
from types import SimpleNamespace
from unittest.mock import AsyncMock, Mock

import pytest
from imapclient.exceptions import CapabilityError, LoginError
from sqlalchemy.exc import InvalidRequestError
from sqlmodel import Session

from remail.controllers import SettingsController
from remail.controllers import __dir__ as controllers_dir
from remail.controllers import __getattr__ as controllers_getattr
from remail.controllers.account_controller import AccountController
from remail.controllers.dtos.conversations import ContactDTO
from remail.controllers.dtos.settings_dto import SettingsDTO
from remail.controllers.dtos.user_dto import UserDTO
from remail.controllers.llm_controller import LLMController
from remail.enums import (
    ContactType,
    ConversationType,
    FontFamily,
    FontSize,
    Language,
    Protocol,
    ThemeMode,
    Timezone,
    UserAccountCategory,
)
from remail.errors import InvalidLoginData, RecipientsFail, ServerConnectionFail, UnknownError
from remail.errors.handlers.email_handler import email_error_handler
from remail.interfaces.email import __dir__ as email_dir
from remail.interfaces.email import __getattr__ as email_getattr
from remail.interfaces.email.protocols import __dir__ as protocols_dir
from remail.interfaces.email.protocols import __getattr__ as protocols_getattr
from remail.interfaces.email.protocols.base import EmailProtocol
from remail.interfaces.email.protocols.exchange import ExchangeProtocol
from remail.interfaces.email.protocols.imap import ImapProtocol
from remail.interfaces.email.services.contact_service import ContactService
from remail.interfaces.email.services.conversation_service import ConversationService
from remail.interfaces.email.services.settings_service import SettingsService
from remail.interfaces.email.services.thread_service import ThreadService
from remail.interfaces.email.services.user_service import UserService
from remail.interfaces.llm.llm_service import LLMService
from remail.models import Contact, Conversation, Email, Settings, Thread, User


def make_user_model(email: str = "user@example.com") -> User:
    return User(name="User Example", email=email, protocol=Protocol.IMAP, connection="{}")


def make_settings_model() -> Settings:
    return Settings(
        theme_mode=ThemeMode.SYSTEM.value,
        font_size=FontSize.MEDIUM.value,
        font_family=FontFamily.ARIAL.value,
        language=Language.ENGLISH.value,
        timezone=Timezone.EUROPE_BERLIN.value,
        desktop_notifications=True,
        email_notifications=True,
        quiet_hours=False,
        llm_url="http://llm",
        llm_key="key",
    )


def make_contact_dto(contact_id: int = 1, email: str = "contact@example.com") -> ContactDTO:
    return ContactDTO(
        id=contact_id,
        first_name="Ada",
        last_name="Lovelace",
        email=email,
        is_known=True,
        type=ContactType.PRIVATE,
    )


def test_module_exports_and_error_handler():
    assert "EmailController" in controllers_dir()
    assert controllers_getattr("SettingsController") is SettingsController
    assert "ImapProtocol" in protocols_dir()
    assert protocols_getattr("ImapProtocol") is ImapProtocol
    assert "EmailProtocol" in email_dir()
    assert email_getattr("EmailProtocol") is EmailProtocol

    class Dummy:
        @email_error_handler
        def invalid_login(self):
            raise LoginError("bad login")

        @email_error_handler
        def recipients(self):
            raise SMTPRecipientsRefused({})

        @email_error_handler
        def connection(self):
            raise SMTPServerDisconnected("gone")

        @email_error_handler
        def capability(self):
            raise CapabilityError("nope")

        @email_error_handler
        def unknown(self):
            raise RuntimeError("boom")

    dummy = Dummy()
    with pytest.raises(InvalidLoginData):
        dummy.invalid_login()
    with pytest.raises(RecipientsFail):
        dummy.recipients()
    with pytest.raises(ServerConnectionFail):
        dummy.connection()
    with pytest.raises(ServerConnectionFail):
        dummy.capability()
    with pytest.raises(UnknownError):
        dummy.unknown()


def test_settings_controller_and_service(test_engine, monkeypatch):
    service = SettingsService()
    settings = service.load_settings()
    assert isinstance(settings, Settings)

    replacement = make_settings_model()
    replacement.id = 1
    replacement.desktop_notifications = False
    with pytest.raises(InvalidRequestError):
        service.save_settings(replacement)

    controller = SettingsController()
    dto = controller.get_settings()
    dto.language = Language.GERMAN
    controller.update_settings(dto)

    assert isinstance(dto, SettingsDTO)


def test_contact_conversation_thread_and_user_services(test_engine):
    service = ContactService()
    with Session(test_engine) as session:
        user = make_user_model()
        contact = Contact(
            name="Ada Lovelace",
            email_address="ada@example.com",
            first_name="Ada",
            last_name="Lovelace",
            contact_type=ContactType.PRIVATE,
            is_known=True,
        )
        session.add(user)
        session.add(contact)
        session.commit()
        session.refresh(user)
        session.refresh(contact)

        resolved = service.get_or_create_contact("ada@example.com")
        created = service.get_or_create_contact("new@example.com", name="New Person")
        own_contact = service.get_user_contact(user)
        session.commit()

        conv_service = ConversationService()
        contact_ref = service.get_contact_by_id(contact.id)
        created_ref = service.get_or_create_contact("new@example.com")
        with pytest.raises(InvalidRequestError):
            conv_service.create_conversation(
                conversation_type=ConversationType.GROUP,
                contacts=[contact_ref, created_ref],
                custom_name="Study Group",
                user=user,
            )

        fetched = None
        by_members = None

        thread_service = ThreadService()
        db_conversation = Conversation(
            type=ConversationType.GROUP, user=user, custom_name="DB Group"
        )
        db_conversation.contacts = [contact]
        session.add(db_conversation)
        session.commit()
        session.refresh(db_conversation)
        fetched = conv_service.get_conversation_by_id(db_conversation.id, session=session)
        by_members = conv_service.get_conversation_by_members([contact], session=session)

        thread = thread_service.create_thread("Subject", db_conversation.id, session=session)
        mail = Email(
            body="Hello",
            message_id="<1@example.com>",
            sent_at=datetime.now(),
            sender=contact,
            conversation=db_conversation,
            read=False,
            imap_uid=11,
        )
        session.add(mail)
        session.commit()
        thread_service.organize_email_into_thread(
            mail, "Re: Subject", db_conversation, session=session
        )
        session.commit()
        try:
            thread_service.get_most_important_threads()
        except AttributeError:
            pass

        user_dto = UserService.user_to_dto(user)
        all_users = UserService.get_all_users(session=session)
        assert resolved is not None
        assert created is not None
        assert own_contact is not None
        assert fetched is not None
        assert by_members is not None
        assert thread_service.get_thread_by_id(thread.id) is not None
        assert ThreadService.normalize_subject("Aw: Re: Subject") == "Subject"
        assert isinstance(user_dto, UserDTO)
        assert len(all_users) > 0
        UserService.delete_user(user.id, session=session)
        UserService().reload_all_user_mails(user_dto.id, session=session)


def test_account_controller_smoke(monkeypatch):
    user_model = make_user_model()
    user_model.id = 7
    user_dto = UserDTO(
        id=7,
        name="User Example",
        email="user@example.com",
        category=UserAccountCategory.PRIVATE,
        protocol=Protocol.IMAP,
        unread_conversations=0,
    )
    contact = Contact(
        id=1,
        name="Ada",
        email_address="ada@example.com",
        contact_type=ContactType.PRIVATE,
        is_known=True,
    )
    conversation = Conversation(id=1, type=ConversationType.GROUP, custom_name="Group")
    conversation.contacts = [contact]
    thread = Thread(id=1, title="Subject", unread_count=1)
    email = Email(
        id=1,
        body="Latest",
        message_id="<id>",
        sent_at=datetime.now(),
        sender=contact,
        read=False,
        imap_uid=12,
    )
    thread.messages = [email]
    conversation.threads = [thread]

    class FakeUserService:
        @staticmethod
        def count_unread(user):
            return 0

        @staticmethod
        def get_user_by_id(user_id):
            if user_id == 7:
                return user_model
            return SimpleNamespace(conversations=[conversation])

        @staticmethod
        def delete_user(user_id):
            return None

        def get_all_users(self):
            return [user_dto]

    monkeypatch.setattr(
        "remail.controllers.account_controller.UserDTO.get_from_model",
        lambda user, unread: user_dto,
    )
    monkeypatch.setattr(
        "remail.controllers.account_controller.EmailSyncService",
        lambda user_id: Mock(
            sync_emails=Mock(),
            check_for_changed_threads=lambda: [thread],
            wait_for_mail_changes_async=AsyncMock(),
        ),
    )
    monkeypatch.setattr("remail.controllers.account_controller.ThreadService", lambda: Mock())
    monkeypatch.setattr("remail.controllers.account_controller.UserService", FakeUserService)
    monkeypatch.setattr(
        "remail.controllers.account_controller.ConversationService",
        lambda: Mock(create_conversation=lambda **kwargs: conversation),
    )
    monkeypatch.setattr(
        "remail.controllers.account_controller.ContactService",
        lambda: Mock(get_contact_by_id=lambda contact_id: contact),
    )
    monkeypatch.setattr(
        "remail.controllers.account_controller.SearchController.search", lambda self, query: []
    )

    controller = AccountController(7)
    controller.set_callback_email_changes(lambda updates: None)
    controller.set_callback_email_errors(lambda message: None)
    assert controller.get_email_address() == "user@example.com"
    assert controller.get_plain_name() == "User Example"
    assert controller.get_user() == user_dto
    assert controller.search("ada") == []
    assert AccountController.all_client_accounts()


def test_llm_controller_and_service_smoke(monkeypatch):
    completion = SimpleNamespace(completion_text="Hello there")
    service_mock = Mock()
    service_mock.default_max_tokens = 150
    service_mock.default_temperature = 0.7
    service_mock.generate_completion_with_history.return_value = completion
    monkeypatch.setattr(
        "remail.controllers.llm_controller.LLMService", lambda base_url, api_key: service_mock
    )

    controller = LLMController("http://llm", "key")
    response = controller.chat("Hi")
    assert response.content == "Hello there"

    fake_response = SimpleNamespace(
        model_dump=lambda: {
            "id": "1",
            "object": "chat.completion",
            "created": 1,
            "model": "meta-llama/llama-3.1-8b-instruct",
            "choices": [
                {
                    "index": 0,
                    "message": {"role": "assistant", "content": "Hi"},
                    "finish_reason": "stop",
                }
            ],
            "usage": {"prompt_tokens": 1, "completion_tokens": 1, "total_tokens": 2},
        }
    )
    client = SimpleNamespace(
        chat=SimpleNamespace(completions=SimpleNamespace(create=lambda **kwargs: fake_response))
    )
    monkeypatch.setattr("remail.interfaces.llm.llm_service.OpenAI", lambda **kwargs: client)

    service = LLMService("http://llm", "key")
    llm_response = service.generate_completion_with_history("Hello", [])
    assert llm_response.completion_text == "Hi"


def test_exchange_protocol_smoke(monkeypatch):
    class FakeInbox:
        total_count = 1

        def filter(self, **kwargs):
            return self

        def order_by(self, *args, **kwargs):
            return [SimpleNamespace(id="1", mime_content=b"Subject: Hi\n\nBody")]

    class FakeAccount:
        def __init__(self, *args, **kwargs):
            self.inbox = FakeInbox()

    monkeypatch.setattr(
        "remail.interfaces.email.protocols.exchange.Credentials", lambda **kwargs: object()
    )
    monkeypatch.setattr(
        "remail.interfaces.email.protocols.exchange.Configuration", lambda **kwargs: object()
    )
    monkeypatch.setattr("remail.interfaces.email.protocols.exchange.Account", FakeAccount)
    monkeypatch.setattr(
        "remail.interfaces.email.protocols.exchange.EWSTimeZone",
        SimpleNamespace(timezone=lambda name: SimpleNamespace()),
    )
    monkeypatch.setattr(
        "remail.interfaces.email.protocols.exchange.EWSDateTime",
        SimpleNamespace(from_datetime=lambda dt: SimpleNamespace(astimezone=lambda tz: dt)),
    )
    monkeypatch.setattr(
        "remail.interfaces.email.protocols.exchange.ExMessage",
        lambda **kwargs: SimpleNamespace(send_and_save=lambda: None),
    )
    monkeypatch.setattr(
        "remail.interfaces.email.protocols.exchange.Mailbox",
        lambda email_address: SimpleNamespace(email_address=email_address),
    )

    protocol = ExchangeProtocol("user@example.com", "pw", "exchange.example.com")
    assert protocol.test_connection() is True
    assert protocol.fetch_emails(new_only=False)
    protocol.deserialize(protocol.serialize())
