"""Service for syncing emails from IMAP to the database."""

from __future__ import annotations

import logging
from collections.abc import AsyncGenerator
from typing import TYPE_CHECKING

from sqlmodel import Session, col, select

from remail.enums import Protocol
from remail.interfaces.email import EmailProtocol, ImapProtocol
from remail.interfaces.email.services import EmailParser
from remail.models import (
    Conversation,
    Email,
    User,
)
from remail.utils.session_management import session
from remail.utils.timer import Timer
from remail.interfaces.email.protocols.exchange import ExchangeProtocol


if TYPE_CHECKING:
    from remail.interfaces.email.services.email_parser import EmailParser


class EmailSyncService:
    """Service for syncing emails from IMAP server to the local database."""

    _logger = logging.getLogger(__name__)

    def __init__(
        self,
        user_id: int,
    ):
        """
        Initialize email sync service.

        Args:
            user_id: Database user id (preferred if available)
        """

        self.changed_conversation_ids: list[int] = []
        self.user_id = user_id
        self.email_parser = EmailParser(user_id)
        self.protocol = self._create_protocol()
        self.changed_threads: list[
            int
        ] = []  # list of mails(uid) that were changed after the frontend checked for the last time

    @session
    def _create_protocol(self, session: Session) -> EmailProtocol:
        user = session.get(User, self.user_id)
        if not user:
            raise RuntimeError("User not found for sync process")
        if user.protocol == Protocol.IMAP:
            try:
                return ImapProtocol(serialized=user.connection)
            except Exception as e:
                raise RuntimeError(
                    f"User (id={user.id}) has invalid protocol string: {str(e)}"
                ) from e
        elif user.protocol == Protocol.EXCHANGE:
            try:
                return ExchangeProtocol(serialized=user.connection)
            except Exception as e:
                raise RuntimeError(
                    f"User (id={user.id}) has invalid protocol string: {str(e)}"
                ) from e
        else:
            raise NotImplementedError("Error fetching!")

    @session
    def sync_emails(self, session: Session, new_only=True) -> None:
        """
        Sync emails from IMAP server to database.

        Fetches emails from IMAP, creates/updates contacts, organizes into threads,
        and saves everything to the database.

        Args:
            since: Only sync emails after this datetime (uses user's last_refresh if None)

        Returns:
            Dict with sync status and statistics
        """

        synced_count = 0
        skipped_count = 0
        mails = self.protocol.fetch_emails(new_only=new_only)
        total = len(mails)
        if total == 0:
            self._logger.info("No new emails to sync.")
        else:
            self._logger.info("Fetched %d email(s) from IMAP, processing...", total)
        log_every = max(1, total // 10)
        t = Timer()
        for i, (uid, data) in enumerate(mails.items(), start=1):
            try:
                changed, mail_id, conv_id = self.email_parser.parse_mail(data, uid)
                if changed and conv_id is not None:
                    self.changed_conversation_ids.append(conv_id)
                    synced_count += 1
                else:
                    skipped_count += 1
            except Exception:  # nosec
                pass
            if total > 0 and i % log_every == 0 and i < total:
                self._logger.info("  ... %d / %d processed (%s)", i, total, t.elapsed())
        if total > 0:
            self._logger.info(
                "Sync complete: %d new/updated, %d unchanged. (%s)",
                synced_count,
                skipped_count,
                t.elapsed(),
            )
        self._save_connection_data()

    async def wait_for_mail_changes_async(self) -> AsyncGenerator[None, None]:
        async for mails in self.protocol.wait_for_changes():
            changed = False
            for uid, data in mails.items():
                try:
                    changed_mail, mail_id, conv_id = self.email_parser.parse_mail(data, uid)
                    if changed_mail and conv_id is not None:
                        changed = True
                        self.changed_conversation_ids.append(conv_id)
                except Exception:  # nosec
                    pass
            if changed:
                yield None

    @session
    def _save_connection_data(self, session: Session):
        user = session.get(User, self.user_id)
        if user:
            user.connection = self.protocol.serialize()

    @session
    def _email_exists(self, message_id: str, session: Session) -> bool:
        """
        Check if an email with the given message_id already exists.

        Args:
            session: Database session
            message_id: Message-ID header value

        Returns:
            True if email exists, False otherwise
        """
        if not message_id:
            return False

        return session.exec(select(Email).where(Email.message_id == message_id)).first() is not None

    @session
    def get_changed_conversations(self, session: Session) -> list[Conversation]:
        if not self.changed_conversation_ids:
            return []
        result = session.exec(
            select(Conversation).where(col(Conversation.id).in_(self.changed_conversation_ids))
        ).all()
        self.changed_conversation_ids = []
        return list(result)
