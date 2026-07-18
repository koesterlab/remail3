import asyncio
import datetime
import smtplib
from collections.abc import AsyncGenerator, Sequence
from functools import wraps
from typing import Any

from imapclient import IMAPClient

from remail import errors as ee
from remail.enums.auth_methods import AuthMethods
from remail.enums.connection_security import ConnectionSecurity
from remail.errors import email_error_handler
from remail.interfaces.email import EmailProtocol
from remail.interfaces.email.services.folder_service import FolderService
from remail.interfaces.email.services.message_builder import MessageBuilder
from remail.interfaces.email.services.smtp_sender import SmtpSender


class ImapProtocol(EmailProtocol):
    """IMAP/SMTP email protocol implementation."""

    imap_username: str
    imap_password: str
    imap_host: str
    imap_port: int
    imap_method: AuthMethods
    imap_security: ConnectionSecurity
    smtp_username: str
    smtp_password: str
    smtp_host: str
    smtp_port: int
    smtp_method: AuthMethods
    smtp_security: ConnectionSecurity
    fetch_since: int
    use_modcount: bool
    use_idle: bool
    user_username: str
    user_password: str

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
        username: str | None = None,
        password: str | None = None,
        host: str | None = None,
    ):
        self.fields_to_fetch = list(fields_to_fetch)
        if serialized != "{}":
            self.deserialize(serialized)
            self.user_username = self.imap_username
            self.user_password = self.imap_password
            self._logged_in = True
            self._smtp = SmtpSender(
                self.smtp_host,
                self.smtp_username or self.imap_username,
                self.smtp_password or self.imap_password,
            )
        elif username and password and host:
            self.imap_username = username
            self.imap_password = password
            self.imap_host = host
            self.imap_port = 993
            self.imap_method = AuthMethods.PASSWORD
            self.imap_security = ConnectionSecurity.SSL_TLS
            self.smtp_username = username
            self.smtp_password = password
            self.smtp_host = host
            self.smtp_port = 587
            self.smtp_method = AuthMethods.PASSWORD
            self.smtp_security = ConnectionSecurity.SSL_TLS
            self.fetch_since = 0
            self.use_modcount = False
            self.use_idle = False
            self.user_username = username
            self.user_password = password
            self._logged_in = False
            self._client = IMAPClient(host, port=993)
            self._smtp = SmtpSender(host, username, password)
            self._folder_service = FolderService(self._client)
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
            self.smtp_port = smtp_port if smtp_port is not None else 587
            self.smtp_method = smtp_method if smtp_method is not None else AuthMethods.PASSWORD
            self.smtp_security = (
                smtp_security if smtp_security is not None else ConnectionSecurity.SSL_TLS
            )

            self.use_modcount = False
            self.use_idle = False
            self.fetch_since = 0

            self.user_username = imap_username
            self.user_password = imap_password
            self._logged_in = True
            self._smtp = SmtpSender(
                smtp_host,
                smtp_username or imap_username,
                smtp_password or imap_password,
            )
        else:
            raise ValueError("Imap Protocol without data or user")

    @property
    def logged_in(self) -> bool:
        return self._logged_in

    @email_error_handler
    def login(self) -> None:
        if not self.user_username or not self.user_password:
            raise ee.InvalidLoginData()
        self._client.login(self.user_username, self.user_password)
        self._logged_in = True

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
                server = smtplib.SMTP(self.smtp_host, self.smtp_port)
                server.starttls()
            else:
                server = smtplib.SMTP(self.smtp_host, self.smtp_port)
                if self.smtp_security == ConnectionSecurity.STARTTLS:
                    server.starttls()
            if self.smtp_method == AuthMethods.PASSWORD:
                smtp_password = self.smtp_password or self.imap_password
                server.login(self.smtp_username, smtp_password)
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
    def test_imap_connection(self, client: IMAPClient) -> bool:
        try:
            client.noop()
            return True
        except Exception:
            return False

    @smtp
    def test_smtp_connection(self, server: smtplib.SMTP,) -> bool:
        try:
            server.noop()
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
            client.select_folder("INBOX")
            if self.fetch_since and new_only:
                criteria = ["SINCE", datetime.datetime.fromtimestamp(self.fetch_since)]  # type:ignore
            else:
                criteria = ["ALL"]
            uids = client.search(criteria)
            self.fetch_since = int(datetime.datetime.now().timestamp())
            raw = client.fetch(uids, self.fields_to_fetch) if uids else {}
            return raw  # type:ignore

    @email_error_handler
    def send_email(self, mail: Any) -> None:
        """
        Sends a mail via SMTP.

        Args:
            mail: Object with .thread.title, .thread.conversation.contacts,
                  .body (str), and .attachments (list with .filename).
        """
        self._smtp.validate_send_state(self.logged_in)
        contacts = mail.thread.conversation.contacts
        to = [f"{c.first_name} {c.last_name} <{c.email_address}>" for c in contacts]
        msg = MessageBuilder.build_message(
            subject=mail.thread.title,
            body=mail.body,
            from_addr=self.user_username,
            to=to,
            cc=[],
        )
        MessageBuilder.attach_files(msg, [a.filename for a in mail.attachments])
        self._smtp.send(msg, [c.email_address for c in contacts])

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
                "smtp_password": self.smtp_password,
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
        self.smtp_password = data.get("smtp_password")
        self.smtp_host = data["smtp_host"]
        self.smtp_port = data["smtp_port"]
        self.smtp_method = AuthMethods[data["smtp_method"]]
        self.smtp_security = ConnectionSecurity[data["smtp_security"]]
        self.fetch_since = data["fetch_since"]
        self.use_modcount = data["use_modcount"]
        self.use_idle = data["use_idle"]
