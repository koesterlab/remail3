import asyncio
import datetime
import logging
import threading
from collections.abc import Callable, Iterable
from typing import cast

from sqlalchemy.orm import selectinload
from sqlmodel import Session, select

from remail import errors as ee
from remail.controllers.dtos.conversations import ContactDTO, ConversationDTO, ThreadPreviewDTO
from remail.controllers.dtos.threads import MessageDTO
from remail.controllers.dtos.user_dto import UserDTO
from remail.controllers.search_controller import SearchController
from remail.enums import ConversationType, Protocol
from remail.interfaces.email import EmailProtocol
from remail.interfaces.email.services import (
    ConversationService,
    EmailSyncService,
    ThreadService,
)
from remail.interfaces.email.services.contact_service import ContactService
from remail.interfaces.email.services.user_service import UserService
from remail.models import Contact, Conversation, Email, Thread, User
from remail.utils.session_management import session
from remail.utils.timer import Timer


class AccountController:
    """Class for base operations for existing users"""

    _logger = logging.getLogger(__name__)

    @staticmethod
    def all_client_accounts() -> list["AccountController"]:
        users = UserService().get_all_users()
        result = [AccountController(dto.id) for dto in users]
        return result

    @staticmethod
    def create_new_account(
        clearname: str, email: str, connection: EmailProtocol, method: Protocol
    ) -> None:
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
        # Receives (task_id, message, progress | None).  Called on sync start,
        # each background tick, and on completion/error so the UI can update the
        # task tray without knowing about the state layer directly.
        self.progress_callback: Callable[[str, str, float | None], None] = lambda *_: None
        # Receives task_id when the sync loop is fully finished so the UI can
        # remove the task entry from the tray.
        self.done_callback: Callable[[str], None] = lambda _: None

        self.search_controller = SearchController()

        threading.Thread(
            target=self.search_controller.index_existing_emails,
            daemon=True,
            name="Old-Emails-Worker",
        ).start()

    @session
    def _get_conversations_from_db(
        self,
        session: Session,
        limit: int = 50,  # Number of conversations to load at a time
        offset: int = 0,  # Start position — used for "Load more" functionality
    ) -> list[ConversationDTO]:
        self._logger.info("[%s] Loading conversations from DB...", self.user.email)
        t = Timer()
        user = session.exec(
            select(User)
            .where(User.id == self.user_id)
            .options(
                selectinload(User.conversations).options(  # type: ignore[arg-type]
                    selectinload(Conversation.threads).selectinload(Thread.messages),  # type: ignore[arg-type]
                    selectinload(Conversation.contacts),  # type: ignore[arg-type]
                )
            )
        ).first()
        if not user:
            return []

        # Only load a limited number of conversations at a time for better performance
        # offset allows loading more conversations when the user clicks "Load more"
        conversations = user.conversations[offset : offset + limit]

        result = [self._conversation_to_dto(c) for c in conversations]
        self._logger.info(
            "[%s] Loaded %d conversation(s) from DB (offset=%d, limit=%d). (%s)",
            self.user.email,
            len(result),
            offset,
            limit,
            t.elapsed(),
        )
        return result

    @session
    def get_conversations(self) -> list[ConversationDTO]:
        """Returns all conversations from the users inbox"""
        self._logger.info("[%s] Syncing emails via IMAP...", self.user.email)
        t = Timer()
        self.sync_service.sync_emails()

        self._logger.info("[%s] IMAP sync complete. (%s)", self.user.email, t.elapsed())
        self._notify_callback()
        # Load only the first 50 conversations by default
        result: list[ConversationDTO] = self._get_conversations_from_db()
        return result

    def set_callback_email_changes(
        self, callback: Callable[[Iterable[ConversationDTO]], None]
    ) -> None:
        """Registers a callback that is called every time when a Conversation is updated or new with the conversation"""
        self.callback = callback

    def update_account(
        self,
        name: str,
        password: str,
        imap_host: str,
        imap_port: int,
        smtp_host: str,
        smtp_port: int,
    ):
        UserService.update_user(
            self.user_id,
            name,
            password,
            imap_host,
            imap_port,
            smtp_host,
            smtp_port,
        )
        self.user.name = name

    def set_callback_email_errors(self, callback: Callable[[str], None]) -> None:
        """Registers a callback that is called when background sync fails."""
        self.error_callback = callback

    def set_callback_progress(self, callback: Callable[[str, str, float | None], None]) -> None:
        """Register a callback that receives sync-progress updates.

        The callback is invoked with ``(task_id, message, progress)`` where
        ``task_id`` is stable for the lifetime of this controller instance,
        ``message`` is a human-readable status string, and ``progress`` is
        a float in ``[0.0, 1.0]`` or ``None`` for an indeterminate state.

        Args:
            callback: Function to call on each progress event.
        """
        self.progress_callback = callback

    def set_callback_done(self, callback: Callable[[str], None]) -> None:
        """Register a callback invoked when the sync loop exits (success or error).

        The callback receives the ``task_id`` so the caller can remove the
        corresponding entry from the task tray.

        Args:
            callback: Function to call when this account's sync loop finishes.
        """
        self.done_callback = callback

    @session
    def _notify_callback(self) -> None:
        changed: list[Conversation] = self.sync_service.get_changed_conversations()
        if changed:
            self._logger.info(
                "[%s] Building DTOs for %d changed conversation(s)...",
                self.user.email,
                len(changed),
            )
            t = Timer()
            dtos = [self._conversation_to_dto(c) for c in changed]
            self._logger.info("[%s] DTO build done. (%s)", self.user.email, t.elapsed())
            self.callback(dtos)

    def _notify_error(self, msg: str) -> None:
        self.error_callback(msg)

    async def start_listening(self) -> None:
        """Starts background task to wait for email changes in imap idle mode. Calls callback if something changes"""
        task_id = f"sync-{self.user.email}"
        try:
            self._logger.info("[%s] Showing cached emails from DB.", self.user.email)
            self.progress_callback(task_id, "Syncing emails...", None)
            self.callback(self._get_conversations_from_db())

            first_sync = True
            while True:
                try:
                    self._logger.info("[%s] Starting IMAP sync...", self.user.email)
                    t = Timer()
                    await asyncio.to_thread(self.sync_service.sync_emails)
                    self._logger.info("[%s] IMAP sync done. (%s)", self.user.email, t.elapsed())
                    self._notify_callback()
                    if first_sync:
                        self.done_callback(task_id)
                        first_sync = False
                    async for _ in self.sync_service.wait_for_mail_changes_async():
                        self._logger.info("[%s] IMAP IDLE: new mail detected.", self.user.email)
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

    def load_more_conversations(self, offset: int) -> list[ConversationDTO]:
        """Load the next batch of conversations starting from the given offset.
        Called when the user clicks 'Load more' in the conversation list.
        """
        result: list[ConversationDTO] = list(self._get_conversations_from_db(offset=offset))
        return result

    @session
    def find_or_create_contact_by_email(self, email: str, session: Session) -> ContactDTO:
        contact = self.contact_service.get_or_create_contact(email)
        session.flush()
        return cast(ContactDTO, ContactDTO.from_model(contact))

    @session
    def create_conversation(self, contacts: list[ContactDTO], session: Session) -> ConversationDTO:
        user = self._get_user_model()
        contact_models = self._get_contact_models(contacts)
        conversation = self.conversation_service.create_conversation(
            conversation_type=ConversationType.GROUP,
            contacts=contact_models,
            custom_name=None,
            user=user,
        )
        session.flush()  # populate conversation.id before building the DTO
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

    @session
    def search(
        self, search_string: str, requested_emails: int = 10, session: Session | None = None
    ) -> list[MessageDTO]:
        email_ids = self.search_controller.search(search_string, requested_emails=requested_emails)

        if not email_ids:
            return []

        result_dtos = []
        seen_conversation_ids = set()

        for email_id in email_ids:
            email = session.get(Email, email_id)  # type: ignore
            if not email or not email.thread:
                continue

            conversation = email.thread.conversation
            if conversation and conversation.id not in seen_conversation_ids:
                seen_conversation_ids.add(conversation.id)
                result_dtos.append(self._conversation_to_dto(conversation))

        return result_dtos
