"""Service for syncing emails from IMAP to the database."""

from __future__ import annotations

from collections.abc import AsyncGenerator
from typing import TYPE_CHECKING

from sqlmodel import Session, col, select

from remail.enums import Protocol
from remail.interfaces.email.services import EmailParser
from remail.interfaces.email import EmailProtocol, ImapProtocol
from remail.models import (
    Email,
    Thread,
    User,
)
from remail.utils.session_management import session

if TYPE_CHECKING:
    from remail.interfaces.email.services.email_parser import EmailParser


class EmailSyncService:
    """Service for syncing emails from IMAP server to the local database."""

    def __init__(
        self,
        user_id: int,
    ):
        """
        Initialize email sync service.

        Args:
            user_id: Database user id (preferred if available)
        """

        self.changed_mails = []
        self.user_id = user_id
        self.email_parser = EmailParser(user_id)
        self.protocol = self._create_protocol()
        self.changed_threads: list[int] = []  # list of mails(uid) that were changed after the frontend checked for the last time

    @session
    def _create_protocol(self, session:Session) -> EmailProtocol:
        user = session.get(User, self.user_id)
        if user.protocol == Protocol.IMAP:
            return ImapProtocol(serialized=user.connection)
        else:
            raise NotImplementedError("Fetching with exchange accounts not implemented")

    @session
    def sync_emails(self, session: Session, new_only = True) -> None:
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
        for uid, data in self.protocol.fetch_emails(new_only=new_only).items():
            try:
                changed, mail = self.email_parser.parse_mail(data, uid)
                if changed:
                    self.changed_mails.append(mail)
                    synced_count += 1
                else:
                    skipped_count += 1
            except ValueError as v:
                pass
        self._save_connection_data()

    @session
    async def wait_for_mail_changes_async(self, session:Session) -> AsyncGenerator[None, None]:
        async for mails in self.protocol.wait_for_changes():
            changed = False
            for uid, data in mails.items():
                changed_mail, mail = self.email_parser.parse_mail(data, uid)
                if changed_mail:
                    changed = True
                    self.changed_mails.append(mail)
            if changed:
                yield None

    @session
    def _save_connection_data(self, session:Session):
        session.get(User, self.user_id).connection = self.protocol.serialize()

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
    def check_for_changed_threads(self, session:Session) -> list[Thread]:
        if self.changed_mails == []:
            return []

        result = session.exec(
            select(Thread)
            .distinct()
            .join(Email, onclause=(col(Thread.id) == col(Email.thread_id)))
            .where(col(Email.imap_uid).in_(self.changed_mails))
        ).all()

        self.changed_mails = []
        return list(result)
