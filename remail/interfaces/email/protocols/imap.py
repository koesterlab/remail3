from __future__ import annotations

import email as py_email
from collections import OrderedDict
from datetime import datetime, timedelta
from email.message import Message

from imapclient import IMAPClient
from imapclient.exceptions import LoginError
from pytz import timezone

from remail import errors as ee
from remail.errors.handlers import email_error_handler
from remail.interfaces.email.protocols.base import EmailProtocol
from remail.interfaces.email.services import (
    EmailParser,
    FolderService,
    MessageBuilder,
    SmtpSender,
)
from remail.models import Email

UTC = timezone("UTC")


class ImapException(Exception):
    def __str__(self):
        return f"Unable to connect to IMAP server: {self.args[0]}"

    pass


class ImapProtocol(EmailProtocol):
    """IMAP/SMTP email protocol implementation."""

    def __init__(
        self,
        username: str | None,
        password: str | None,
        host: str,
    ):
        """
        Initialize IMAP protocol.

        Args:
            username: Login username
            password: User password
            host: IMAP/SMTP server hostname
        """
        self.user_username: str | None = username
        self.user_password: str | None = password
        self.host = host
        self._logged_in = False
        try:
            self.IMAP = IMAPClient(self.host, use_uid=True, ssl=True)
        except Exception as e:
            raise ImapException(e) from e

        # Initialize services
        self.folder_service = FolderService(self.IMAP)
        self.email_parser = EmailParser()
        self.smtp_sender = SmtpSender(host, username, password)

    @property
    def logged_in(self) -> bool:
        """Return True if logged in."""

        return self._logged_in

    @email_error_handler
    def login(self) -> None:
        """Log in to IMAP server."""

        if self.logged_in:
            return

        if self.user_password is None or self.user_username is None:
            raise ee.InvalidLoginData() from None

        try:
            self.IMAP.login(self.user_username, self.user_password)
            self._logged_in = True

        except LoginError:
            raise ee.InvalidLoginData() from None

    def logout(self) -> None:
        if not self.logged_in:
            return
        self.IMAP.logout()

    @email_error_handler
    def fetch_emails(
        self,
        folder: str | None = None,
        since: datetime | None = None,
        flags: list[str] | None = None,
    ) -> list[tuple[int, Message]]:
        """
        Fetch emails only (no flag mutations).

        Args:
            folder: mailbox name or None for all user folders.
            since: datetime filter (server uses day granularity; we recheck precisely).
            flags: IMAP search terms (e.g., ["UNSEEN"], ["SEEN"], ["DELETED"],
                ["HEADER","From","x@y"]).
        """

        if not self.logged_in:
            raise ee.NotLoggedIn()
        if since:
            since = max(since, datetime.now() - timedelta(days=365))
        boxes = [folder] if folder else self.folder_service.get_all_folders()
        criteria = FolderService.build_search_criteria(since, flags)
        out: list[tuple[int, Message[str, str]]] = []

        for box in boxes:
            with self.folder_service.selected_folder(box):
                uids = self.IMAP.search(criteria)

                if not uids:
                    continue

                fetched = self.IMAP.fetch(uids, ["RFC822"])

            for uid, data in fetched.items():
                try:
                    em = py_email.message_from_bytes(data[b"RFC822"])

                    if since:
                        dt = self.email_parser.extract_msg_date(em)

                        if not isinstance(dt, datetime):
                            dt = getattr(em, "dt", None)

                        cutoff = since.astimezone(UTC)

                        if isinstance(dt, datetime):
                            try:
                                if dt.tzinfo is None:
                                    from pytz import UTC as _UTC

                                    dt_utc = _UTC.localize(dt)

                                else:
                                    dt_utc = dt.astimezone(UTC)

                                if dt_utc < cutoff:
                                    continue

                            except Exception:  # nosec B112
                                continue

                    out.append((int(uid), em))  # self.email_parser.parse_email_message(em, uid))
                except Exception as e:
                    print(e)

        return out

    def send_email(self, mail: Email) -> None:
        """Send email via SMTP."""

        self.smtp_sender.validate_send_state(self.logged_in)
        thread = mail.thread
        conversation = thread.conversation
        recipients = conversation.contacts

        msg = MessageBuilder.build_message(
            subject=mail.thread.title or "",
            body=mail.body or "",
            from_addr=self.user_username or "",
            to=[f"{c.first_name} {c.last_name} <{c.email_address}>" for c in recipients],
            cc=[],
        )

        if mail.attachments:
            MessageBuilder.attach_files(msg, (a.filename for a in mail.attachments))

        ordered_recipients: list[str] = [c.email_address for c in recipients]
        envelope = list(OrderedDict.fromkeys(ordered_recipients).keys())

        self.smtp_sender.send(msg, envelope)

    def clone(self):
        return ImapProtocol(self.user_username, self.user_password, self.host)
