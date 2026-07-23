# EVERYTHING HERE IS UNCHECKED #

import asyncio
import json
from collections.abc import AsyncGenerator
from datetime import UTC, datetime
from typing import Any
from zoneinfo import ZoneInfo

from exchangelib import (
    DELEGATE,
    Account,
    Configuration,
    Credentials,
    Mailbox,
)
from exchangelib import Message as ExMessage

from remail.interfaces.email import EmailProtocol
from remail.models.email import Email  # angenommen, dein Email-Datentyp


class ExchangeProtocol(EmailProtocol):
    """Exchange email protocol implementation using exchangelib."""

    def __init__(self, username="", password="", server="", serialized="{}"):
        if serialized != "{}":
            self.deserialize(serialized)
        else:
            self.username = username
            self.password = password
            self.server = server
            self.tz = ZoneInfo("UTC")
            self.last_fetch = datetime.min
            creds = Credentials(username=username, password=password)
            config = Configuration(server=server, credentials=creds)
            self.account = Account(
                primary_smtp_address=username,
                config=config,
                autodiscover=False,
                access_type=DELEGATE,
            )

    # ------------------------
    # Interface Methods
    # ------------------------
    def test_connection(self) -> bool:
        try:
            _ = self.account.inbox.total_count
            return True
        except Exception:
            return False

    def fetch_emails(self, new_only: bool = True) -> dict[Any, Any]:
        if new_only and self.last_fetch != datetime.min:
            items = self.account.inbox.filter(datetime_received__gte=self.last_fetch).order_by(
                "datetime_received"
            )
        else:
            items = self.account.inbox.all()
        messages: dict[Any, Any] = {}
        for item in items:
            raw_bytes = item.mime_content
            messages[str(item.id)] = {
                b"BODY[]": raw_bytes,
                b"FLAGS": (b"\\Seen",) if item.is_read else (),
            }
        self.last_fetch = datetime.now(tz=UTC)
        return messages

    def send_email(self, email: Email) -> None:
        msg = ExMessage(
            account=self.account,
            subject=email.thread,
            body=email.body,
            to_recipients=[
                Mailbox(email_address=c.email_address) for c in email.thread.conversation.contacts
            ],
        )
        msg.send_and_save()

    def clone(self) -> "EmailProtocol":
        return ExchangeProtocol(self.username, self.password, self.server)

    async def wait_for_changes(self) -> AsyncGenerator[dict[Any, Any], None]:
        """
        Wait for live updates. Best-effort implementation using polling,
        returns list of (item_id, email.message.Message) tuples.
        """
        while True:
            emails = self.fetch_emails(self.last_fetch)
            if emails:
                yield emails
            # Exchange unterstützt keine native IDLE, daher Polling
            await asyncio.sleep(30)  # check alle 30 Sekunden

    def serialize(self) -> str:
        return json.dumps(
            {"username": self.username, "password": self.password, "server": self.server}
        )

    def deserialize(self, string: str) -> None:
        data = json.loads(string)
        self.username = data["username"]
        self.password = data["password"]
        self.server = data["server"]
        self.tz = ZoneInfo("UTC")
        self.last_fetch = datetime.min
        creds = Credentials(username=self.username, password=self.password)
        config = Configuration(server=self.server, credentials=creds)
        self.account = Account(
            primary_smtp_address=self.username,
            config=config,
            autodiscover=False,
            access_type=DELEGATE,
        )
