import asyncio
import datetime
import logging
from collections.abc import Callable, Iterable
from typing import cast

from remail import errors as ee
from remail.controllers.dtos.conversations import ContactDTO, ConversationDTO, ThreadPreviewDTO
from remail.controllers.dtos.user_dto import UserDTO
from remail.enums import ConversationType, Protocol
from remail.interfaces.email import EmailProtocol
from remail.interfaces.email.services import (
    ConversationService,
    EmailSyncService,
    ThreadService,
)
from remail.interfaces.email.services.contact_service import ContactService
from remail.interfaces.email.services.user_service import UserService
from remail.models import Contact, Conversation, User
from remail.utils.session_management import session


class AccountController:
    """Class for base operations for existing users"""

    _logger = logging.getLogger(__name__)

    @staticmethod
    def all_client_accounts() -> list["AccountController"]:
        users = UserService().get_all_users()
        return [AccountController(dto.id) for dto in users]

    @staticmethod
    def create_new_account(
        clearname: str, email: str, connection: EmailProtocol, method: Protocol
    ) -> None:
        if not connection.test_connection():
            raise ValueError("Creating account with invalid credentials")
        UserService().add_user(email, clearname, method, connection)

    @session
    def __init__(self, account_id: int) -> None:
        self.user_id = account_id
        self.user_service = UserService()
        self.conversation_service = ConversationService()
        self.contact_service = ContactService()
        self.thread_service = ThreadService()

        user = self._get_user_model()
        self.user: UserDTO = UserDTO.get_from_model(user, UserService.count_unread(user))
        self.sync_service = EmailSyncService(user_id=self.user.id)
        self.callback: Callable[[Iterable[ConversationDTO]], None] = lambda _: None
        self.error_callback: Callable[[str], None] = lambda _: None

    @session
    def get_conversations(self) -> list[ConversationDTO]:
        """Returns all conversations from the users inbox"""
        # re-sync via imap
        self.sync_service.sync_emails()

        # notify callback if something has changed
        self._notify_callback()

        # return all conversation DTOs
        return [self._conversation_to_dto(e) for e in self._get_user_model().conversations]

    def set_callback_email_changes(
        self, callback: Callable[[Iterable[ConversationDTO]], None]
    ) -> None:
        """Registers a callback that is called every time when a Conversation is updated or new with the conversation"""
        self.callback = callback

    def set_callback_email_errors(self, callback: Callable[[str], None]) -> None:
        """Registers a callback that is called when background sync fails."""
        self.error_callback = callback

    @session
    def _notify_callback(self) -> None:
        changed: list[Conversation] = self.sync_service.get_changed_conversations()
        if changed:
            self.callback([self._conversation_to_dto(c) for c in changed])

    def _notify_error(self, msg: str) -> None:
        self.error_callback(msg)

    async def start_listening(self) -> None:
        """Starts background task to wait for email changes in imap idle mode. Calls callback if something changes"""
        try:
            print("Starting sync service")
            self.callback(self.get_conversations())
            print("First sync over")

            while True:
                try:
                    async for _ in self.sync_service.wait_for_mail_changes_async():
                        self._notify_callback()
                except ee.InvalidLoginData:
                    raise  # propagate – cannot recover from bad credentials
                except Exception as exc:
                    self._logger.warning(
                        "Sync connection lost for %s (%s), reconnecting in 30 s",
                        self.user.email,
                        exc,
                    )
                    await asyncio.sleep(30)
                    self.sync_service = EmailSyncService(user_id=self.user.id)
        except ee.InvalidLoginData:
            self._notify_error("Invalid login credentials")
        except Exception as exc:
            self._logger.exception("Background sync stopped for %s", self.user.email)
            self._notify_error(f"Sync stopped: {exc}")

    def get_email_address(self) -> str:
        return str(self.user.email)

    def get_plain_name(self) -> str:
        return str(self.user.name)

    def get_user(self) -> UserDTO:
        return self.user

    @session
    def create_conversation(self, contacts: list[ContactDTO]) -> ConversationDTO:
        user = self._get_user_model()
        contact_models = self._get_contact_models(contacts)
        conversation = self.conversation_service.create_conversation(
            conversation_type=ConversationType.GROUP,
            contacts=contact_models,
            custom_name=None,
            user=user,
        )
        return cast(ConversationDTO, ConversationDTO.from_model(conversation, user))

    def delete(self) -> None:
        UserService.delete_user(self.user_id)

    def _get_user_model(self) -> User:
        user = self.user_service.get_user_by_id(self.user_id)
        if user is None:
            raise ValueError(f"Account with id {self.user_id} not found")
        return cast(User, user)

    def _get_contact_models(self, contacts: list[ContactDTO]) -> list[Contact]:
        contact_models: list[Contact] = []
        for contact in contacts:
            contact_model = self.contact_service.get_contact_by_id(contact.id)
            if contact_model is None:
                raise ValueError(f"Contact with id {contact.id} not found")
            contact_models.append(contact_model)
        return contact_models

    @session
    def _conversation_to_dto(self, conversation: Conversation) -> ConversationDTO:
        threads = []
        for thread in conversation.threads:
            unread_count = 0
            total_count = 0
            latest_message = None
            for message in thread.messages:
                if not message.read:
                    unread_count += 1
                if not latest_message or message.sent_at > latest_message.sent_at:
                    latest_message = message
                total_count += 1
            threads.append(
                ThreadPreviewDTO(
                    thread_id=thread.id if thread.id is not None else -1,
                    title=thread.title,
                    total_count=total_count,
                    unread_count=unread_count,
                    last_message=latest_message.body if latest_message else "",
                    last_message_datetime=latest_message.sent_at
                    if latest_message
                    else datetime.datetime.min,
                )
            )

        return ConversationDTO(
            id=conversation.id if conversation.id is not None else -1,
            is_favorite=conversation.is_favorite,
            custom_name=conversation.custom_name,
            contacts=[
                ContactDTO(
                    id=c.id if c.id is not None else -1,
                    first_name=c.first_name or "",
                    last_name=c.last_name or c.name,
                    email=c.email_address,
                    is_known=c.is_known,
                    type=c.contact_type,
                )
                for c in conversation.contacts
                if c.email_address != self.user.email
            ],
            threads=threads,
        )

    def search(self, search_string: str) -> list[ConversationDTO]:
        return []  # todo
