import asyncio
import datetime
import smtplib
from collections.abc import AsyncGenerator, Sequence
from email.message import EmailMessage
from email.utils import formataddr, make_msgid
from functools import wraps
from typing import Any

from imapclient import IMAPClient

from remail.enums.auth_methods import AuthMethods
from remail.enums.connection_security import ConnectionSecurity
from remail.interfaces.email import EmailProtocol


class ImapProtocol(EmailProtocol):
    """IMAP/SMTP email protocol implementation."""

    def __init__(
        self,
        imap_username: str | None = None,
        imap_password: str | None = None,
        imap_host: str | None = None,
        imap_port: int = 993,
        imap_method: AuthMethods = AuthMethods.PASSWORD,
        imap_security: ConnectionSecurity = ConnectionSecurity.SSL_TLS,
        smtp_username: str | None = None,
        smtp_password: str | None = None,
        smtp_host: str | None = None,
        smtp_port: int | None = 587,
        smtp_method: AuthMethods | None = AuthMethods.PASSWORD,
        smtp_security: ConnectionSecurity | None = ConnectionSecurity.SSL_TLS,
        serialized: str = "{}",
        fields_to_fetch: Sequence[str] = (
            "BODY.PEEK[]",  # body of the message
            "FLAGS",  # flags
            "INTERNALDATE",  # server-date
        ),
    ):
        self.fields_to_fetch = list(fields_to_fetch)
        if serialized != "{}":
            self.deserialize(serialized)
        elif (
            imap_username
            and imap_password
            and imap_host
            and smtp_username
            and smtp_password
            and smtp_host
        ):
            self.imap_username = imap_username
            self.imap_password = imap_password
            self.imap_host = imap_host
            self.imap_port = imap_port
            self.imap_method = imap_method
            self.imap_security = imap_security
            self.last_fetch = datetime.datetime.min

            self.smtp_username = smtp_username
            self.smtp_password = smtp_password
            self.smtp_host = smtp_host
            self.smtp_port = smtp_port
            self.smtp_method = smtp_method
            self.smtp_security = smtp_security

            self.use_modcount = False
            self.use_idle = False
            self.fetch_since: int = 0

        else:
            raise ValueError("Imap Protocol without data or user")

    # ------------------------
    # IMAP decorator
    # ------------------------

    def _connect_to_imap(self, client: IMAPClient):
        resp = b""
        if self.imap_security == ConnectionSecurity.STARTTLS:
            resp = client.starttls()
        if self.imap_method == AuthMethods.PASSWORD:
            resp = client.login(self.imap_username, self.imap_password)
        elif self.imap_method == AuthMethods.OAUTH:
            resp = client.oauth2_login(self.imap_username, self.imap_password)
        self.use_idle = b"IDLE" in resp  # supports IMAP IDLE extension -> "live Updates"
        self.use_modcount = (
            b"CONDSTORE" in resp
        )  # supports IMAP Condstore Extension -> version numbers for changes
        if self.use_modcount:
            client.enable(b"CONDSTORE")

    @staticmethod
    def imap(func):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            ssl = self.imap_security == ConnectionSecurity.SSL_TLS
            with IMAPClient(self.imap_host, port=self.imap_port, ssl=ssl) as client:
                ImapProtocol._connect_to_imap(self, client)
                return func(self, client, *args, **kwargs)

        return wrapper

    # ------------------------
    # SMTP decorator
    # ------------------------
    @staticmethod
    def smtp(func):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            ssl = self.smtp_security == ConnectionSecurity.SSL_TLS
            if ssl:
                server = smtplib.SMTP_SSL(self.smtp_host, self.smtp_port)
            else:
                server = smtplib.SMTP(self.smtp_host, self.smtp_port)
                if self.smtp_security == ConnectionSecurity.STARTTLS:
                    server.starttls()
            if self.smtp_method == AuthMethods.PASSWORD:
                server.login(self.smtp_username, self.smtp_password)
            try:
                return func(self, server, *args, **kwargs)
            finally:
                server.quit()

        return wrapper

    # ------------------------
    # Interface Methods
    # ------------------------
    @imap
    def test_connection(self, client: IMAPClient) -> bool:
        try:
            client.noop()
            return True
        except Exception:
            return False

    @imap
    def fetch_emails(
        self, client: IMAPClient, new_only: bool = True
    ) -> dict[int, dict[bytes, Any]]:
        """Retrieve emails from server."""
        if self.use_modcount:
            folder_info = client.select_folder("INBOX")
            modcount = folder_info[b"HIGHESTMODSEQ"]
            if str(modcount) == str(self.fetch_since) and new_only:
                return {}  # no new mods
            uids = client.search(["ALL"])
            if self.fetch_since and new_only:  # there is already a modcount, fetch since then
                criteria = ["CHANGEDSINCE", str(self.fetch_since)]
            else:
                criteria = None
            self.fetch_since = modcount  # setze fetch_since auf highest modcount
            return client.fetch(uids, self.fields_to_fetch, criteria)  # type:ignore
        else:
            if self.fetch_since and new_only:
                criteria = ["SINCE", datetime.datetime.fromtimestamp(self.fetch_since)]  # type:ignore
            else:
                criteria = ["ALL"]
            uids = client.search(criteria)
            self.fetch_since = int(datetime.datetime.now().timestamp())
            raw = client.fetch(uids, self.fields_to_fetch) if uids else []
            return raw  # type:ignore

    @smtp
    def send_email(
        self,
        server: smtplib.SMTP,
        sender: tuple[str, str],
        recipients: list[tuple[str, str]],
        subject: str,
        msg: str,
    ) -> None:
        """
        Sends a mail
        #todo not tested
        #todo support cc, bcc
        #todo support attachments

        Args:
            server: The SMTP-Server (filled by annotation)
            sender: The sender (name, mail)
            recipients: the accounts to send the mail to [(name, mail)]
            subject: The mail subject
            msg: The (plaintext) message
        """
        email = EmailMessage()

        # Header
        email["From"] = formataddr(sender)
        email["To"] = ", ".join(formataddr(r) for r in recipients)
        email["Subject"] = subject
        email["Message-ID"] = make_msgid()

        # Body (plain text)
        email.set_content(msg)

        # SMTP send
        server.send_message(email)

    def clone(self) -> "EmailProtocol":
        return ImapProtocol(
            imap_username=self.imap_username,
            imap_password=self.imap_password,
            imap_host=self.imap_host,
            imap_port=self.imap_port,
            imap_method=self.imap_method,
            imap_security=self.imap_security,
            smtp_username=self.smtp_username,
            smtp_password=self.smtp_password,
            smtp_host=self.smtp_host,
            smtp_port=self.smtp_port,
            smtp_method=self.smtp_method,
            smtp_security=self.smtp_security,
        )

    async def wait_for_changes(self) -> AsyncGenerator[dict[int, dict[bytes, Any]], None]:
        if self.use_idle:
            ssl = self.imap_security == ConnectionSecurity.SSL_TLS
            with IMAPClient(self.imap_host, port=self.imap_port, ssl=ssl) as client:
                self._connect_to_imap(client)  # cannot use imap annotation because of async actions
                client.select_folder("INBOX")
                client.idle()
                try:
                    while True:
                        changes = client.idle_check(timeout=60)  # 1 min timeout
                        if [
                            c for c in changes if len(c) > 1 and isinstance(c[0], int)
                        ]:  # if email-related update found
                            updated_mails = self.fetch_emails(new_only=True)
                            if updated_mails:
                                yield updated_mails
                        await asyncio.sleep(1)
                finally:
                    client.idle_done()
        else:  # fetch periodically
            while True:
                await asyncio.sleep(60)  # fetch every minute
                result = self.fetch_emails(new_only=True)
                if result:
                    yield result

    def serialize(self) -> str:
        import json

        return json.dumps(
            {
                "imap_username": self.imap_username,
                "imap_password": self.imap_password,
                "imap_host": self.imap_host,
                "imap_port": self.imap_port,
                "imap_method": self.imap_method.name,
                "imap_security": self.imap_security.name,
                "smtp_username": self.smtp_username,
                "smtp_host": self.smtp_host,
                "smtp_port": self.smtp_port,
                "smtp_method": self.smtp_method.name if self.smtp_method else "password",
                "smtp_security": self.smtp_security.name if self.smtp_security else "ssl_tls",
                "fetch_since": self.fetch_since,
                "use_idle": self.use_idle,
                "use_modcount": self.use_modcount,
            }
        )

    def deserialize(self, string: str) -> None:
        import json

        data = json.loads(string)
        self.imap_username = data["imap_username"]
        self.imap_password = data["imap_password"]
        self.imap_host = data["imap_host"]
        self.imap_port = data["imap_port"]
        self.imap_method = AuthMethods[data["imap_method"]]
        self.imap_security = ConnectionSecurity[data["imap_security"]]
        self.smtp_username = data["smtp_username"]
        self.smtp_host = data["smtp_host"]
        self.smtp_port = data["smtp_port"]
        self.smtp_method = AuthMethods[data["smtp_method"]]
        self.smtp_security = ConnectionSecurity[data["smtp_security"]]
        self.fetch_since = data["fetch_since"]
        self.use_modcount = data["use_modcount"]
        self.use_idle = data["use_idle"]
