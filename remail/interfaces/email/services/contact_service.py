"""Service for managing contacts."""

from __future__ import annotations

from sqlmodel import Session, col, select

from remail.database import engine
from remail.enums import ContactType
from remail.models import Contact, ConversationContact, UserConversation


class ContactService:
    """Service for managing contacts."""

    def __init__(self) -> None:
        """Initialize contact service."""
        self.engine = engine

    def get_all_contacts(self, user_id: int) -> list[Contact]:
        """
        Fetch all contacts associated with a user.

        Args:
            user_id: User ID to fetch contacts for

        Returns:
            List of Contact models
        """
        with Session(self.engine) as session:
            contacts = session.exec(
                select(Contact)
                .join(
                    ConversationContact,
                    col(Contact.id) == col(ConversationContact.contact_id),
                )
                .join(
                    UserConversation,
                    col(ConversationContact.conversation_id)
                    == col(UserConversation.conversation_id),
                )
                .where(UserConversation.user_id == user_id)
                .distinct()
            ).all()

            return list(contacts)

    def get_contact_by_id(self, contact_id: int) -> Contact | None:
        """
        Fetch a contact by ID.

        Args:
            contact_id: Contact ID to fetch

        Returns:
            Contact model instance, or None if not found
        """
        with Session(self.engine) as session:
            return session.get(Contact, contact_id)

    def create_contact(
        self,
        email: str,
        first_name: str | None = None,
        last_name: str | None = None,
        contact_type: ContactType = ContactType.PRIVATE,
        is_known: bool = True,
        name: str | None = None,
    ) -> Contact | None:
        """
        Create a new contact if one does not already exist.

        Args:
            email: Contact email address
            first_name: Contact first name (optional)
            last_name: Contact last name (optional)
            contact_type: Contact type category
            is_known: Whether the contact is known/registered
            name: Full name override (optional)

        Returns:
            Contact instance, or None if email is empty
        """
        email_address = (email or "").lower().strip()

        if not email_address:
            return None

        with Session(self.engine) as session:
            existing = session.exec(
                select(Contact).where(Contact.email_address == email_address)
            ).first()

            if existing:
                return existing

            resolved_name = name
            if not resolved_name:
                if first_name or last_name:
                    resolved_name = f"{first_name or ''} {last_name or ''}".strip()
                if not resolved_name:
                    resolved_name = email_address.split("@")[0]

            if first_name is None and last_name is None and name:
                parts = name.strip().split()
                if len(parts) == 1:
                    first_name = parts[0]
                    last_name = ""
                elif len(parts) > 1:
                    first_name = parts[0]
                    last_name = " ".join(parts[1:])

            contact = Contact(
                name=resolved_name,
                email_address=email_address,
                first_name=first_name,
                last_name=last_name,
                contact_type=contact_type,
                is_known=is_known,
            )

            session.add(contact)
            session.commit()
            session.refresh(contact)

            return contact
