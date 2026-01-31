"""Service for syncing emails from IMAP to the database."""

from __future__ import annotations

import traceback
from collections.abc import AsyncGenerator, Callable
from datetime import datetime
from typing import TYPE_CHECKING

from sqlmodel import Session, col, select

from remail.database import engine
from remail.interfaces.email import EmailProtocol, ImapProtocol
from remail.interfaces.email.services.user_service import UserService
from remail.models import (
    Conversation,
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
        protocol: EmailProtocol,
        email_parser: EmailParser,
        user_id: int | None = None,
        username: str | None = None,
    ):
        """
        Initialize email sync service.

        Args:
            protocol: IMAP protocol instance for fetching emails
            email_parser: Email parser for extracting email data
            user_id: Database user id (preferred if available)
            username: Username to resolve a user id when user_id is not provided
        """

        self.engine = engine
        if user_id is None:
            if not username:
                raise ValueError("user_id or username is required for syncing")
            user = UserService.get_user_by_username(username)
            if not user or user.id is None:
                raise ValueError(f"User not found for username: {username}")
            user_id = user.id
        self.user_id = user_id
        self.protocol = protocol
        self.email_parser = email_parser
        self.changed_mails: list[
            int
        ] = []  # list of mails(uid) that were changed after the frontend checked for the last time

    @session
    def sync_emails(self, session: Session, since: datetime | None = None) -> dict:
        """
        Sync emails from IMAP server to database.

        Fetches emails from IMAP, creates/updates contacts, organizes into threads,
        and saves everything to the database.

        Args:
            since: Only sync emails after this datetime (uses user's last_refresh if None)

        Returns:
            Dict with sync status and statistics
        """

        user = session.get(User, self.user_id)
        if not user:
            return {
                "status": "error",
                "message": f"User with id {self.user_id} not found",
                "synced_count": 0,
            }
        # Determine the cutoff date for fetching
        fetch_since = since or user.last_refresh

        # Fetch emails from IMAP
        try:
            if not self.protocol.logged_in:
                self.protocol.login()
            raw_emails = self.protocol.fetch_emails(since=fetch_since)

        except Exception as e:
            return {
                "status": "error",
                "message": f"Failed to fetch emails: {str(e)}",
                "synced_count": 0,
            }

        if not raw_emails:
            user.last_refresh = datetime.now()

            return {
                "status": "success",
                "message": "No new emails to sync",
                "synced_count": 0,
            }

        synced_count = 0
        skipped_count = 0

        for uid, raw_email in raw_emails:
            try:
                message_id = raw_email.get("Message-ID")

                if message_id and self._email_exists(message_id):
                    skipped_count += 1
                    continue

                # Process and save the email
                self.email_parser.process_email(raw_email, user, uid)
                synced_count += 1

            except Exception as e:
                print(f"Error processing email: {e}")
                traceback.print_exc()
                continue

        # Update user's last_refresh timestamp
        user.last_refresh = datetime.now()

        return {
            "status": "success",
            "message": f"Synced {synced_count} email(s), skipped {skipped_count} duplicate(s)",
            "synced_count": synced_count,
            "skipped_count": skipped_count,
        }

    async def wait_for_mail_changes_async(self) -> AsyncGenerator[None, None]:
        # clone protocol because connection will always be blocked
        protokol = self.protocol.clone()
        if not isinstance(protokol, ImapProtocol):
            return
        protokol.login()
        IMAP = protokol.IMAP
        if not IMAP:
            return
        IMAP.select_folder("INBOX")  # TODO: find inbox folder
        IMAP.idle()
        last_refresh = datetime.now()
        while True:
            for update in IMAP.idle_check():
                if update[0] == b"EXISTS":
                    self.sync_emails(since=last_refresh)
                elif update[0] == b"EXPUNGE":

                    def delete(mail: Email) -> None:
                        mail.deleted = True

                    self._update_mail_data(update[1], delete)
                elif update[0] == b"FLAGS":
                    # msgid = update[1][0]
                    # flags = update[1][1]
                    # TODO: inspect FLAGS data
                    pass
                # signal that something happened
                yield None

    def _update_mail_data(self, uid: int, modifier: Callable[[Email], None]):
        self.changed_mails.append(uid)
        with Session(engine) as session:
            mail = session.exec(select(Email).where(Email.imap_uid == uid)).first()
            if mail is None:
                return
            modifier(mail)
            session.commit()
            session.refresh(mail)

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

    def check_for_changed_conversations(self) -> list[Conversation]:
        if self.changed_mails == []:
            return []
        with Session(self.engine) as session:
            result = session.exec(
                select(Conversation)
                .distinct()
                .join(Thread, onclause=(col(Conversation.id) == col(Thread.conversation_id)))
                .join(Email, onclause=(col(Thread.id) == col(Email.thread_id)))
                .where(col(Email.imap_uid).in_(self.changed_mails))
            ).all()

        self.changed_mails = []
        return list(result)
