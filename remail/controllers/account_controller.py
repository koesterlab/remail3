import datetime
import logging
from collections.abc import Callable, Iterable

from remail import errors as ee
from remail.controllers import EmailController
from remail.controllers.dtos.conversations import ContactDTO, ConversationDTO, ThreadPreviewDTO
from remail.controllers.dtos.user_dto import UserDTO
from remail.interfaces.email.protocols.imap import ImapException, ImapProtocol
from remail.interfaces.email.services import (
    ConversationService,
    EmailParser,
    EmailSyncService,
    ThreadService,
)
from remail.interfaces.email.services.user_service import UserService
from remail.models import Conversation
from remail.utils.session_management import session


class AccountController:
    """Class for base operations for existing users"""

    _logger = logging.getLogger(__name__)

    @staticmethod
    def all_client_accounts() -> list["AccountController"]:
        users = UserService.get_all_users()
        # With lazy IMAP connect, AccountController() no longer fails just because host is bad.
        return [AccountController(dto.id) for dto in users]

    @session
    def __init__(self, account_id: int):
        self.user_id = account_id
        self.user: UserDTO = UserService.get_user_by_id(account_id)

        password = UserService.get_user_password(self.user.username)
        if password is None:
            self._logger.warning("No stored password for %s", self.user.username)

        # IMPORTANT: ImapProtocol is now lazy-connect; it won't connect until login().
        self.protocol: ImapProtocol = ImapProtocol(
            username=self.user.username,
            password=password,
            host=self.user.host,
        )

        self.sync_service = EmailSyncService(
            protocol=self.protocol,
            email_parser=EmailParser(),
            user_id=self.user.id,
        )
        self.thread_service = ThreadService()
        self.user_service = UserService()
        self.conversation_service = ConversationService()

        self.callback: Callable[[Iterable[ConversationDTO]], None] = lambda _: None
        self.error_callback: Callable[[str], None] = lambda _: None

    @session
    def get_conversations(self) -> Iterable[ConversationDTO]:
        """Returns all conversations (sync via IMAP if possible, otherwise DB-only)."""

        # Try sync; if it fails, fall back to DB state.
        try:
            self.sync_service.sync_emails()
        except ee.InvalidLoginData:
            self._logger.warning("Invalid login for %s; DB-only mode", self.user.email)
            self._notify_error("Invalid login credentials")
        except (ImapException, OSError) as exc:
            self._logger.warning("IMAP unavailable for %s; DB-only mode: %s", self.user.email, exc)
            self._notify_error(f"IMAP unavailable (DB-only): {exc}")
        except Exception as exc:
            # Don't kill UI for unexpected sync issues
            self._logger.exception("Sync failed for %s; DB-only mode", self.user.email)
            self._notify_error(f"Sync failed (DB-only): {exc}")

        # notify callback if something has changed (only meaningful if sync succeeded)
        try:
            self._notify_callback()
        except Exception:
            # Never break the UI because change detection failed
            self._logger.debug("check_for_changed_conversations failed", exc_info=True)

        # return all conversation DTOs from DB
        conversations_data = self.conversation_service.get_all_conversations(self.user.id)
        return [self._conversation_to_dto(e) for e in conversations_data]

    def _notify_error(self, msg: str) -> None:
        """Forward sync errors to UI layer."""
        self.error_callback(msg)

    def set_callback_email_changes(
        self, callback: Callable[[Iterable[ConversationDTO]], None]
    ) -> None:
        """Called when conversation updates are detected."""
        self.callback = callback

    def set_callback_email_errors(self, callback: Callable[[str], None]) -> None:
        """Called when background sync fails."""
        self.error_callback = callback

    def _notify_callback(self) -> None:
        changed = self.sync_service.check_for_changed_conversations()
        if len(changed) > 0:
            self.callback(changed)

    async def start_listening(self) -> None:
        """Starts background task to wait for email changes in IMAP idle mode."""
        self._logger.info("Starting sync service for %s", self.user.email)

        # Always try to render UI from DB at least once
        try:
            self.callback(self.get_conversations())
        except Exception:
            # UI should still not die even if callback/view layer fails
            self._logger.exception("Initial conversation callback failed for %s", self.user.email)

        # Now try to enter IMAP idle loop; if it fails, just stop listening silently.
        try:
            async for _ in self.sync_service.wait_for_mail_changes_async():
                try:
                    self._notify_callback()
                except Exception:
                    self._logger.debug("notify callback failed", exc_info=True)

        except ee.InvalidLoginData:
            self._notify_error("Invalid login credentials")
            self._logger.warning("Invalid login for %s; stop IMAP listening", self.user.email)

        except (ImapException, OSError) as exc:
            self._notify_error(f"IMAP connection failed: {exc}")
            self._logger.warning("IMAP connection failed for %s; stop listening", self.user.email)

        except Exception as exc:
            self._notify_error(f"Sync stopped: {exc}")
            self._logger.exception("Background sync stopped for %s", self.user.email)

    def get_email_address(self) -> str:
        return self.user.email

    def get_plain_name(self) -> str:
        return self.user.name

    def get_user(self) -> UserDTO:
        return self.user

    def get_email_controller(self) -> EmailController:
        if self.protocol.user_username is None or self.protocol.user_password is None:
            raise ValueError("Missing protocol credentials")
        return EmailController(
            self.protocol.user_username, self.protocol.user_password, self.protocol.host
        )

    @session
    def _conversation_to_dto(self, conversation: Conversation) -> ConversationDTO:
        threads: list[ThreadPreviewDTO] = []

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
