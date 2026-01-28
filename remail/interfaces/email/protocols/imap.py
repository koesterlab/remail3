from __future__ import annotations

import email as py_email
from collections import OrderedDict
from datetime import datetime

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
    RecipientService,
    SmtpSender,
)
from remail.models import Email

UTC = timezone("UTC")


class ImapProtocol(EmailProtocol):
    """IMAP/SMTP email protocol implementation."""

    def __init__(
        self,
        username: str,
        password: str,
        host: str,
    ):
        """
        Initialize IMAP protocol.

        Args:
            username: Username/email address
            password: User password
            host: IMAP/SMTP server hostname
        """

        self.user_username: str | None = username
        self.user_password: str | None = password
        self.host = host
        self._logged_in = False
        self.IMAP = IMAPClient(self.host, use_uid=True, ssl=True)

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

    @email_error_handler
    def fetch_emails(
        self,
        folder: str | None = None,
        since: datetime | None = None,
        flags: list[str] | None = None,
    ) -> list[Email]:
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

        boxes = [folder] if folder else self.folder_service.get_user_folders()
        criteria = FolderService.build_search_criteria(since, flags)
        out: list[Email] = []

        for box in boxes:
            with self.folder_service.selected_folder(box):
                uids = self.IMAP.search(criteria)

                if not uids:
                    continue

                fetched = self.IMAP.fetch(uids, ["RFC822"])

            for _, data in fetched.items():
                em = py_email.message_from_bytes(data[b"RFC822"])

                if since:
                    dt = self.email_parser.safe_msg_datetime(em)

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

                out.append(self.email_parser.parse_email_message(em))

        return out

    def send_email(self, mail: Email) -> None:
        """Send email via SMTP."""

        self.smtp_sender.validate_send_state(self.logged_in)

        to, cc, bcc = RecipientService.split_recipients(mail)

        if not (to or cc or bcc):
            raise ValueError("No recipients provided.")

        msg = MessageBuilder.build_message(
            subject=mail.subject or "",
            body=mail.body or "",
            from_addr=self.user_username or "",
            to=to,
            cc=cc,
        )

        if mail.attachments:
            MessageBuilder.attach_files(msg, (a.filename for a in mail.attachments))

        ordered_recipients = [*to, *cc, *bcc]
        envelope = list(OrderedDict.fromkeys(ordered_recipients).keys())

        self.smtp_sender.send(msg, envelope)
