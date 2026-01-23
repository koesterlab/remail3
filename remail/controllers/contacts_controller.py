"""Contacts controller for managing contact operations."""

from __future__ import annotations

from remail.controllers.dtos.conversations import ContactDTO
from remail.enums import ContactType
from remail.interfaces.email.services.contact_service import ContactService
from remail.interfaces.email.services.conversation_service import ConversationService


class ContactsController:
    """Controller for contact operations."""

    def __init__(self) -> None:
        """Initialize contacts controller."""
        self.service = ContactService()
        self.conversation_service = ConversationService()

    def get_all_contacts(self, user_id: int) -> list[ContactDTO]:
        """
        Fetch all contacts for a specific user.

        Args:
            user_id: User ID to fetch contacts for

        Returns:
            List of ContactDTO objects
        """
        contacts = self.service.get_all_contacts(user_id)

        return [
            ContactDTO(
                id=contact.id,  # type: ignore[arg-type]
                first_name=contact.first_name or "",
                last_name=contact.last_name or "",
                email=contact.email_address,
                is_known=contact.is_known,
                type=contact.contact_type,
            )
            for contact in contacts
        ]

    def create_contact(
        self,
        user_id: int,
        email: str,
        first_name: str | None = None,
        last_name: str | None = None,
        contact_type: ContactType | str = ContactType.PRIVATE,
        is_known: bool = True,
        name: str | None = None,
    ) -> ContactDTO | None:
        """
        Create a new contact.

        Args:
            user_id: User ID creating the contact
            email: Contact email address
            first_name: Contact first name (optional)
            last_name: Contact last name (optional)
            contact_type: Contact type category
            is_known: Whether the contact is known/registered
            name: Full name override (optional)

        Returns:
            ContactDTO for the created/existing contact, or None if invalid input
        """
        resolved_type = (
            contact_type if isinstance(contact_type, ContactType) else ContactType(contact_type)
        )

        contact = self.service.create_contact(
            email=email,
            first_name=first_name,
            last_name=last_name,
            contact_type=resolved_type,
            is_known=is_known,
            name=name,
        )

        if not contact or contact.id is None:
            return None

        self.conversation_service.create_conversation(
            user_id=user_id,
            contact_ids=[contact.id],
        )

        return ContactDTO(
            id=contact.id,
            first_name=contact.first_name or "",
            last_name=contact.last_name or "",
            email=contact.email_address,
            is_known=contact.is_known,
            type=contact.contact_type,
        )
