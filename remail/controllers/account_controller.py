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
from remail.models import Conversation, Thread
from remail.utils.session_management import session


class AccountController:
    """Class for base operations for existing users"""

    _logger = logging.getLogger(__name__)

    @staticmethod
    def all_client_accounts() -> list["AccountController"]:
        users = UserService().get_all_users()
        return [AccountController(dto.id) for dto in users]

    @staticmethod
    def create_new_account(clearname: str, email: str, connection: EmailProtocol, method: Protocol):
        if not connection.test_connection():
            raise ValueError("Creating account with invalid credentials")
        UserService().add_user(email, clearname, method, connection)

    def get_connection_data(self) -> dict[str, str]:
        connection = cast(
            dict[str, str] | None,
            UserService.get_connection_by_user_id(self.user_id),
        )

        if connection is None:
            return {}

        return connection

    @session
    def __init__(self, account_id: int):
        self.user_id = account_id
        user = UserService.get_user_by_id(account_id)
        self.user: UserDTO = UserDTO.get_from_model(user, UserService.count_unread(user))
        self.sync_service = EmailSyncService(user_id=self.user.id)
        self.thread_service = ThreadService()
        self.user_service = UserService()
        self.conversation_service = ConversationService()
        self.contact_service = ContactService()
        self.callback: Callable[[Iterable[ConversationDTO]], None] = lambda _: None
        self.error_callback: Callable[[str], None] = lambda _: None

    @session
    def get_conversations(self) -> Iterable[ConversationDTO]:
        """Returns all conversations from the users inbox"""
        # re-sync via imap
        self.sync_service.sync_emails()

        # notify callback if something has changed
        self._notify_callback()

        # return all conversation DTOs
        return [
            self._conversation_to_dto(e)
            for e in self.user_service.get_user_by_id(self.user_id).conversations
        ]

    def set_callback_email_changes(
        self, callback: Callable[[Iterable[ConversationDTO]], None]
    ) -> None:
        """Registers a callback that is called every time when a Conversation is updated or new with the conversation"""
        self.callback = callback

    def update_account(
        self,
        name: str,
        password: str,
    ):
        UserService.update_user(
            self.user_id,
            name,
            password,
        )

    def set_callback_email_errors(self, callback: Callable[[str], None]) -> None:
        """Registers a callback that is called when background sync fails."""
        self.error_callback = callback

    @session
    def _notify_callback(self):
        changed: list[Thread] = self.sync_service.check_for_changed_threads()
        if len(changed) > 0:
            self.callback(ConversationDTO.from_model(c.conversation) for c in changed)

    def _notify_error(self, msg: str) -> None:
        self.error_callback(msg)

    async def start_listening(self):
        """Starts background task to wait for email changes in imap idle mode. Calls callback if something changes"""
        try:
            print("Starting sync service")
            self.callback(self.get_conversations())
            print("First sync over")

            async for _ in self.sync_service.wait_for_mail_changes_async():
                self._notify_callback()
        except ee.InvalidLoginData:
            self._notify_error("Invalid login credentials")
        except Exception as exc:
            self._logger.exception("Background sync stopped for %s", self.user.email)
            self._notify_error(f"Sync stopped: {exc}")

    def get_email_address(self) -> str:
        return self.user.email

    def get_plain_name(self) -> str:
        return self.user.name

    def get_user(self):
        return self.user

    @session
    def create_conversation(self, contacts: list[ContactDTO]):
        return ConversationDTO.from_model(
            self.conversation_service.create_conversation(
                conversation_type=ConversationType.GROUP,
                contacts=[self.contact_service.get_contact_by_id(c.id) for c in contacts],
                custom_name=None,
                user=self.user_service.get_user_by_id(self.user_id),
            )
        )

    def delete(self):
        UserService.delete_user(self.user_id)

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
