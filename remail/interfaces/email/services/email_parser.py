from datetime import datetime
from email import message_from_bytes
from email.header import decode_header, make_header
from email.message import Message
from email.utils import getaddresses, parsedate_to_datetime
from typing import cast, Any

from pytz import timezone
from sqlmodel import Session, select

from remail.enums import ContactType, ConversationType, RecipientKind
from remail.interfaces.email.services.attachment_service import save_attachment
from remail.interfaces.email.services.contact_service import ContactService
from remail.models import Contact, Conversation, Email, EmailReception, User
from remail.utils.session_management import session

from . import ConversationService
from . import ThreadService
UTC = timezone("UTC")


class EmailParser:

    """Service for parsing email messages."""
    def __init__(self, user_id:int):
        """Initialize email parser."""
        self.user_id = user_id
        self.contact_service = ContactService()
        self.conversation_service = ConversationService()
        self.thread_service = ThreadService()

    @session
    def parse_mail(self, mail_data:dict, imap_uid: int, session:Session) -> tuple[bool, Email]:
        """
        Parses the mail from raw imap data. Updates an existing entry or creates a new one (with thread and conversation if necessary)

        Args:
            mail_data: the imap response with at least body, flags, internaldate,
            imap_uid: the imap uid of the mail (not included in the data!)
            session: DB Session with @session
        """
        msg_id = message_from_bytes(mail_data[b"BODY[]"]).get("Message-ID").strip().lower()
        if not msg_id:
            raise ValueError("Emails without message-id cannot be processed")
        existing = session.exec(select(Email).where(Email.message_id == msg_id)).first()
        if existing:
            return self._update_mail_data(existing, mail_data)
        else:
            return True, self.process_new_email(mail_data, imap_uid)

    @session
    def _update_mail_data(self, existing:Email, mail_data:dict) -> tuple[bool,Email]:
        """
        Updates an existing Mail in the Database. AtM, only seen and deleted state are watched

        Args:
            existing: The db email model (active session)
            mail_data: the corresponding raw imap data with FLAGS
        """
        #msg = message_from_bytes(mail_data[b"BODY[]"])
        flags = mail_data[b"FLAGS"]
        read = b"\\Seen" in flags
        deleted = b"\\Deleted" in flags
        changed = existing.read != read or existing.deleted != deleted
        existing.read = read
        existing.deleted = deleted
        return changed, existing


    @session
    def process_new_email(self, mail_data: dict[bytes, Any], uid: int, session: Session) -> Email:
        """
        Process a raw email and save to database.

        Args:
            raw_email: Raw email entry from the imap fetch (with at least FLAGS, BODY[])
            uid: imap_uid of mail
            session: DB session
        Returns:
            Saved Email instance
        """
        user:User = session.get(User, self.user_id) #type:ignore
        raw_email = message_from_bytes(mail_data[b"BODY[]"])
        flags = mail_data[b"FLAGS"]


        # Extract sender info
        [sender_contact] = self._extract_participant(raw_email, "From")

        # Extract recipients
        to_recipients = self._extract_participant(raw_email, "To")
        cc_recipients = self._extract_participant(raw_email, "CC")
        bcc_recipients = self._extract_participant(raw_email, "BCC")

        # Get all participant contacts (excluding the user themselves)
        all_participants = set([sender_contact] + to_recipients + cc_recipients + bcc_recipients)

        # Remove user's own email from participants if present
        all_participants.discard(self.contact_service.get_user_contact(user))

        # Find or create conversation based on participants
        conversation = self._get_or_create_conversation(list(all_participants), user)
        # Create the email record
        sent_at = self.extract_msg_date(raw_email)
        body = self._get_body(raw_email)
        message_id = raw_email.get("Message-ID").strip().lower()

        db_email = Email(
            imap_uid=uid,
            message_id=message_id,
            body=body,
            sent_at=sent_at,
            sender=sender_contact,
            thread=None,  # type: ignore
            deleted=b"\\Deleted" in flags,
            read=b"\\Seen" in flags,
        )
        session.add(db_email)

        self.thread_service.organize_email_into_thread(
            email=db_email, conversation=conversation, subject=raw_email.get("Subject", "unknown")
        )

        # Ensure email has a primary key before creating dependent rows
        session.flush()

        # Create EmailReception records for all recipients
        self._create_email_receptions(db_email, to_recipients, cc_recipients, bcc_recipients)

        return db_email

    def _extract_participant(self, raw_email: Message, key: str) -> list[Contact]:
        """
        Extract email account information from raw email header.

        Args:
            raw_email: Raw email object
            key: header key where to search for user(s)

        Returns:
            Contact objects from the database that was found or new created
        """
        raw_values = raw_email.get_all(key, [])
        if not raw_values:
            return []
        decoded_values = [self._decode_header_value(v) for v in raw_values]
        addr = getaddresses(decoded_values)
        if not addr:
            return []

        participants: list[Contact] = []
        for name, email in addr:
            decoded_name = self._decode_header_value(name).strip() if name else ""
            decoded_email = self._decode_header_value(email).strip() if email else ""
            if not decoded_email and "@" in decoded_name:
                decoded_email = decoded_name
                decoded_name = ""
            if not decoded_email or "@" not in decoded_email:
                continue
            participants.append(
                self.contact_service.get_or_create_contact(decoded_email, name=decoded_name or None)
            )

        return participants

    @staticmethod
    def _decode_header_value(value: str) -> str:
        try:
            return str(make_header(decode_header(value)))
        except Exception:
            return value

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

    @staticmethod
    def _parse_name(full_name: str) -> tuple[str, str]:
        """
        Parse a full name into first and last name.

        Args:
            full_name: Full name string

        Returns:
            Tuple of (first_name, last_name)
        """
        parts = full_name.strip().split()

        if len(parts) == 0:
            return "", ""

        elif len(parts) == 1:
            return parts[0], ""

        else:
            return parts[0], " ".join(parts[1:])

    def _get_or_create_conversation(self, contacts: list[Contact], user: User) -> Conversation:
        """
        Find existing conversation with the same contacts or create new one.

        Args:
            contacts: List of participant contacts
            user: Current user

        Returns:
            Conversation instance
        """
        conversation = self.conversation_service.get_conversation_by_members(contacts)
        if not conversation:
            conversation = self.conversation_service.create_conversation(
                conversation_type=ConversationType.CONVERSATION
                if len(contacts) == 1
                else ConversationType.GROUP,
                contacts=contacts,
                custom_name=None,
                user=user,
            )
        return cast(Conversation, conversation)

    def _get_body(self, em: Message) -> str:
        body_text: str = ""
        html_parts: list[str] = []
        attachments: list[str] = []
        message_id = em.get("Message-ID").strip().lower() or "unknown"

        if em.is_multipart():
            for part in em.walk():
                dispo = (part.get_content_disposition() or "").lower()
                ctype = (part.get_content_type() or "").lower()
                charset = part.get_content_charset() or "utf-8"

                if dispo == "attachment":
                    filename = str(make_header(decode_header(part.get_filename() or "")))
                    payload = part.get_payload(decode=True)

                    if isinstance(payload, bytes):
                        attachments.append(save_attachment(filename, payload, message_id))

                    continue

                if ctype == "text/html":
                    payload = part.get_payload(decode=True)

                    if isinstance(payload, bytes):
                        html_parts.append(payload.decode(charset, errors="replace"))

                    continue

                if ctype == "text/plain" and dispo != "attachment" and not body_text:
                    payload = part.get_payload(decode=True)

                    if isinstance(payload, bytes):
                        body_text = payload.decode(charset, errors="replace")

                    continue
        else:
            charset = em.get_content_charset() or "utf-8"
            payload = em.get_payload(decode=True)

            if em.get_content_type() == "text/html":
                if isinstance(payload, bytes):
                    html_parts.append(payload.decode(charset, errors="replace"))
            else:
                if isinstance(payload, bytes):
                    body_text = payload.decode(charset, errors="replace")
                else:
                    body_text = ""
        return body_text

    @staticmethod
    def extract_msg_date(em: Message) -> datetime | None:
        """
        Safely extract datetime from email message.

        Args:
            em: Email message object

        Returns:
            Datetime in UTC or None if extraction fails
        """

        try:
            hdr = em.get("Date")

            if hdr:
                dt = parsedate_to_datetime(hdr)
                dt = dt.astimezone(UTC)
                dt = dt.replace(tzinfo=None)  # isnt stored in the database
                return dt

        except Exception:
            return None

        return None

    @session
    def _create_email_receptions(
            self,
            email: Email,
            to_recipients: list[Contact],
            cc_recipients: list[Contact],
            bcc_recipients: list[Contact],
            session: Session,
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

        already_added = set()
        for category, contacts in (
                (RecipientKind.TO, to_recipients),
                (RecipientKind.CC, cc_recipients),
                (RecipientKind.BCC, bcc_recipients),
        ):
            for contact in contacts:
                if contact in already_added:
                    continue
                already_added.add(contact)
                reception = EmailReception(
                    kind=category,
                    email=email,
                    contact=contact,
                )
                session.add(reception)
