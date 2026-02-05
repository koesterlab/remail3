# EVERYTHING HERE IS UNCHECKED #

import json
import asyncio
from datetime import datetime
from typing import AsyncGenerator, Any, List, Tuple
from email import message_from_bytes
from exchangelib import Account, Credentials, DELEGATE, Configuration, Message as ExMessage, Mailbox, EWSDateTime, EWSTimeZone

from remail.interfaces.email import EmailProtocol
from remail.models.email import Email  # angenommen, dein Email-Datentyp


class ExchangeProtocol(EmailProtocol):
    """Exchange email protocol implementation using exchangelib."""

    def __init__(self, username: str, password: str, server: str):
        self.username = username
        self.password = password
        self.server = server
        self.tz = EWSTimeZone.timezone('UTC')
        self.last_fetch = datetime.min

        creds = Credentials(username=username, password=password)
        config = Configuration(server=server, credentials=creds)
        self.account = Account(
            primary_smtp_address=username,
            config=config,
            autodiscover=False,
            access_type=DELEGATE
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

    def fetch_emails(self, since_date: datetime = None) -> List[Tuple[str, Any]]:
        """
        Retrieve emails since `since_date`.
        Returns list of (item_id, email.message.Message)
        """
        if since_date is None:
            since_date = self.last_fetch

        # Convert to Exchange DateTime
        ex_since = EWSDateTime.from_datetime(since_date).astimezone(self.tz)
        items = self.account.inbox.filter(datetime_received__gte=ex_since).order_by('datetime_received')

        messages: List[Tuple[str, Any]] = []
        for item in items:
            # raw MIME message
            raw_bytes = item.mime_content
            msg = message_from_bytes(raw_bytes)
            messages.append((str(item.id), msg))

        self.last_fetch = datetime.utcnow()
        return messages

    def send_email(self, email: Email) -> None:
        msg = ExMessage(
            account=self.account,
            subject=email.subject,
            body=email.body,
            to_recipients=[Mailbox(email_address=a) for a in email.to_addresses]
        )
        msg.send_and_save()

    def clone(self) -> "EmailProtocol":
        return ExchangeProtocol(self.username, self.password, self.server)

    async def wait_for_changes(self) -> AsyncGenerator[List[Tuple[str, Any]], None]:
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
        return json.dumps({
            "username": self.username,
            "server": self.server
        })

    def deserialize(self, string: str) -> None:
        data = json.loads(string)
        self.username = data["username"]
        self.server = data["server"]
        creds = Credentials(username=self.username, password=self.password)
        config = Configuration(server=self.server, credentials=creds)
        self.account = Account(
            primary_smtp_address=self.username,
            config=config,
            autodiscover=False,
            access_type=DELEGATE
        )
