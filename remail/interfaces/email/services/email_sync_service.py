"""Service for syncing emails from IMAP to the database."""

from __future__ import annotations

import re
from datetime import datetime
from typing import TYPE_CHECKING

from sqlmodel import Session, select

from remail.database import engine
from remail.enums import ContactType, ConversationType, RecipientKind
from remail.models import (
    Contact,
    Conversation,
    ConversationContact,
    Email,
    EmailReception,
    Thread,
    User,
    UserConversation,
)

if TYPE_CHECKING:
    from remail.interfaces.email.protocols.imap import ImapProtocol
    from remail.interfaces.email.services.email_parser import EmailParser


class EmailSyncService:
    """Service for syncing emails from IMAP server to the local database."""

    def __init__(
        self,
        protocol: ImapProtocol,
        email_parser: EmailParser,
        user_email: str,
    ):
        """
        Initialize email sync service.

        Args:
            protocol: IMAP protocol instance for fetching emails
            email_parser: Email parser for extracting email data
            user_email: The email address of the current user
        """

        self.protocol = protocol
        self.email_parser = email_parser
        self.user_email = user_email

    def sync_emails(self, since: datetime | None = None) -> dict:
        """
        Sync emails from IMAP server to database.

        Fetches emails from IMAP, creates/updates contacts, organizes into threads,
        and saves everything to the database.

        Args:
            since: Only sync emails after this datetime (uses user's last_refresh if None)

        Returns:
            Dict with sync status and statistics
        """

        with Session(engine) as session:
            # Get or create user
            user = self._get_user(session)

            # Determine the cutoff date for fetching
            fetch_since = since or user.last_refresh

            # Fetch emails from IMAP
            try:
                raw_emails = self.protocol.fetch_emails(since=fetch_since)

            except Exception as e:
                return {
                    "status": "error",
                    "message": f"Failed to fetch emails: {str(e)}",
                    "synced_count": 0,
                }

            if not raw_emails:
                user.last_refresh = datetime.now()
                session.commit()

                return {
                    "status": "success",
                    "message": "No new emails to sync",
                    "synced_count": 0,
                }

            synced_count = 0
            skipped_count = 0

            for raw_email in raw_emails:
                try:
                    message_id = getattr(raw_email, "message_id", None)

                    if message_id and self._email_exists(session, message_id):
                        skipped_count += 1

                        continue

                    # Process and save the email
                    self._process_email(session, raw_email, user)
                    synced_count += 1

                except Exception as e:
                    print(f"Error processing email: {e}")

                    continue

            # Update user's last_refresh timestamp
            user.last_refresh = datetime.now()
            session.commit()

            return {
                "status": "success",
                "message": f"Synced {synced_count} email(s), skipped {skipped_count} duplicate(s)",
                "synced_count": synced_count,
                "skipped_count": skipped_count,
            }

    def _get_user(self, session: Session) -> User:
        """
        Get existing user by email.

        Args:
            session: Database session

        Returns:
            User instance

        Raises:
            ValueError: If user does not exist
        """
        user = session.exec(select(User).where(User.email == self.user_email)).first()

        if not user:
            raise ValueError(f"User with email '{self.user_email}' not found")

        return user

    def _email_exists(self, session: Session, message_id: str) -> bool:
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

    def _process_email(self, session: Session, raw_email, user: User) -> Email:
        """
        Process a raw email and save to database.

        Args:
            session: Database session
            raw_email: Raw email object from parser
            user: Current user

        Returns:
            Saved Email instance
        """
        # Extract sender info
        sender_data = self._extract_sender(raw_email)
        sender_contact = self._get_or_create_contact(session, sender_data)

        # Extract recipients
        to_recipients = self._extract_recipients(raw_email, "to")
        cc_recipients = self._extract_recipients(raw_email, "cc")
        bcc_recipients = self._extract_recipients(raw_email, "bcc")

        # Get all participant contacts (excluding the user themselves)
        all_participants = set()
        all_participants.add(sender_contact.email_address)
        for _name, email in to_recipients + cc_recipients + bcc_recipients:
            all_participants.add(email)

        # Remove user's own email from participants if present
        all_participants.discard(self.user_email)

        # Get or create contacts for all participants
        participant_contacts = [sender_contact]
        for name, email in to_recipients + cc_recipients + bcc_recipients:
            if email != self.user_email and email != sender_contact.email_address:
                contact = self._get_or_create_contact(session, {"name": name, "email": email})
                participant_contacts.append(contact)

        # Find or create conversation based on participants
        conversation = self._get_or_create_conversation(session, participant_contacts, user)

        # Find or create thread based on subject
        subject = getattr(raw_email, "subject", "") or ""
        thread = self._get_or_create_thread(session, subject, conversation, raw_email)

        # Create the email record
        sent_at = getattr(raw_email, "date", None) or datetime.now()
        body = getattr(raw_email, "body", "") or ""
        message_id = getattr(raw_email, "message_id", None)

        db_email = Email(
            message_id=message_id,
            subject=subject,
            body=body,
            sent_at=sent_at,
            sender_id=sender_contact.id,  # type: ignore
            thread_id=thread.id,  # type: ignore
        )
        session.add(db_email)
        session.flush()

        # Create EmailReception records for all recipients
        self._create_email_receptions(
            session, db_email, to_recipients, cc_recipients, bcc_recipients
        )

        # Handle attachments if present
        attachments = getattr(raw_email, "attachments", []) or []
        for attachment in attachments:
            attachment.email_id = db_email.id
            session.add(attachment)

        return db_email

    def _extract_sender(self, raw_email) -> dict:
        """
        Extract sender information from raw email.

        Args:
            raw_email: Raw email object

        Returns:
            Dict with name and email keys
        """
        sender = getattr(raw_email, "sender", None)

        if isinstance(sender, tuple):
            return {"name": sender[0] or "", "email": sender[1] or ""}

        elif isinstance(sender, str):
            return {"name": "", "email": sender}

        elif sender is None:
            return {"name": "Unknown", "email": "unknown@unknown.com"}

        return {"name": "", "email": str(sender)}

    def _extract_recipients(self, raw_email, recipient_type: str) -> list[tuple[str, str]]:
        """
        Extract recipients of a specific type from raw email.

        Args:
            raw_email: Raw email object
            recipient_type: Type of recipient (to, cc, bcc)

        Returns:
            List of (name, email) tuples
        """
        recipients = getattr(raw_email, "recipients", []) or []
        result = []

        for recipient in recipients:
            if isinstance(recipient, tuple) and len(recipient) >= 2:
                kind, name, email = (
                    (recipient[0], recipient[1], recipient[2])
                    if len(recipient) >= 3
                    else (recipient_type, "", recipient[1])
                )
                if str(kind).lower() == recipient_type.lower():
                    result.append((name, email))

        return result

    def _get_or_create_contact(self, session: Session, contact_data: dict) -> Contact:
        """
        Get existing contact or create new one.

        Args:
            session: Database session
            contact_data: Dict with name and email keys

        Returns:
            Contact instance
        """
        email_address = contact_data.get("email", "").lower().strip()
        name = contact_data.get("name", "") or email_address.split("@")[0]

        # Try to find existing contact
        contact = session.exec(
            select(Contact).where(Contact.email_address == email_address)
        ).first()

        if contact:
            return contact

        # Parse name into first/last name
        first_name, last_name = self._parse_name(name)

        # Create new contact
        contact = Contact(
            name=name,
            email_address=email_address,
            first_name=first_name,
            last_name=last_name,
            contact_type=ContactType.PRIVATE,
            is_known=False,  # Discovered contacts start as unknown
        )

        session.add(contact)
        session.flush()

        return contact

    def _parse_name(self, full_name: str) -> tuple[str, str]:
        """
        Parse a full name into first and last name.

        Args:
            full_name: Full name string

        Returns:
            Tuple of (first_name, last_name)
        """
        parts = full_name.strip().split()

        if len(parts) == 0:
            return ("", "")

        elif len(parts) == 1:
            return (parts[0], "")

        else:
            return (parts[0], " ".join(parts[1:]))

    def _get_or_create_conversation(
        self, session: Session, contacts: list[Contact], user: User
    ) -> Conversation:
        """
        Find existing conversation with the same contacts or create new one.

        Args:
            session: Database session
            contacts: List of participant contacts
            user: Current user

        Returns:
            Conversation instance
        """
        contact_ids = {c.id for c in contacts if c.id is not None}

        # Find conversations that have exactly these contacts
        existing_conversations = session.exec(
            select(Conversation).join(UserConversation).where(UserConversation.user_id == user.id)
        ).all()

        for conv in existing_conversations:
            conv_contact_ids = session.exec(
                select(ConversationContact.contact_id).where(
                    ConversationContact.conversation_id == conv.id
                )
            ).all()
            if set(conv_contact_ids) == contact_ids:
                return conv

        # Create new conversation
        conversation_type = (
            ConversationType.GROUP if len(contacts) > 1 else ConversationType.CONVERSATION
        )
        conversation = Conversation(type=conversation_type)

        session.add(conversation)
        session.flush()

        # Link contacts to conversation
        for contact in contacts:
            conv_contact = ConversationContact(
                conversation_id=conversation.id,  # type: ignore
                contact_id=contact.id,  # type: ignore
            )
            session.add(conv_contact)

        # Link user to conversation
        user_conv = UserConversation(
            user_id=user.id,  # type: ignore
            conversation_id=conversation.id,  # type: ignore
            is_favorite=False,
        )

        session.add(user_conv)
        session.flush()

        return conversation

    def _get_or_create_thread(
        self,
        session: Session,
        subject: str,
        conversation: Conversation,
        raw_email,
    ) -> Thread:
        """
        Find existing thread or create new one based on subject.

        Uses subject normalization (removing Re:, Fwd:, etc.) to match related emails.

        Args:
            session: Database session
            subject: Email subject
            conversation: Parent conversation
            raw_email: Raw email for additional threading hints

        Returns:
            Thread instance
        """

        # Normalize subject for matching
        normalized_subject = self._normalize_subject(subject)

        # Try to find existing thread in this conversation with similar subject
        existing_threads = session.exec(
            select(Thread).where(Thread.conversation_id == conversation.id)
        ).all()

        for thread in existing_threads:
            if self._normalize_subject(thread.title) == normalized_subject:
                return thread

        # Create new thread
        thread = Thread(
            title=subject or "No Subject",
            conversation_id=conversation.id,
        )

        session.add(thread)
        session.flush()

        return thread

    def _normalize_subject(self, subject: str) -> str:
        """
        Normalize email subject by removing Re:, Fwd:, etc.

        Args:
            subject: Original subject

        Returns:
            Normalized subject
        """

        if not subject:
            return ""

        # Remove common reply/forward prefixes
        patterns = [
            r"^(re|aw|sv|vs|fw|fwd|wg|tr):\s*",  # Common prefixes
            r"^\[.*?\]\s*",  # Remove [tags]
        ]

        normalized = subject.lower().strip()
        changed = True

        while changed:
            changed = False

            for pattern in patterns:
                new_normalized = re.sub(pattern, "", normalized, flags=re.IGNORECASE)

                if new_normalized != normalized:
                    normalized = new_normalized
                    changed = True

        return normalized.strip()

    def _create_email_receptions(
        self,
        session: Session,
        email: Email,
        to_recipients: list[tuple[str, str]],
        cc_recipients: list[tuple[str, str]],
        bcc_recipients: list[tuple[str, str]],
    ) -> None:
        """
        Create EmailReception records for all recipients.

        Args:
            session: Database session
            email: Email instance
            to_recipients: List of TO recipient (name, email) tuples
            cc_recipients: List of CC recipient (name, email) tuples
            bcc_recipients: List of BCC recipient (name, email) tuples
        """
        for name, addr in to_recipients:
            contact = self._get_or_create_contact(session, {"name": name, "email": addr})
            reception = EmailReception(
                kind=RecipientKind.TO,
                email_id=email.id,  # type: ignore
                contact_id=contact.id,  # type: ignore
            )
            session.add(reception)

        for name, addr in cc_recipients:
            contact = self._get_or_create_contact(session, {"name": name, "email": addr})
            reception = EmailReception(
                kind=RecipientKind.CC,
                email_id=email.id,  # type: ignore
                contact_id=contact.id,  # type: ignore
            )
            session.add(reception)

        for name, addr in bcc_recipients:
            contact = self._get_or_create_contact(session, {"name": name, "email": addr})
            reception = EmailReception(
                kind=RecipientKind.BCC,
                email_id=email.id,  # type: ignore
                contact_id=contact.id,  # type: ignore
            )
            session.add(reception)
