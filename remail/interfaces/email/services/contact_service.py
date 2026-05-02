from typing import cast

from sqlmodel import Session, select

from remail.database import engine
from remail.models import Contact, User
from remail.utils.session_management import session


class ContactService:
    """Service for managing contacts."""

    def __init__(self) -> None:
        """Initialize contact service."""

        self.engine = engine

    @session
    def get_contact_by_id(self, contact_id: int, session: Session) -> Contact | None:
        """
        Fetch a contact by ID.

        Args:
            contact_id: Contact ID to fetch

        Returns:
            Contact model instance, or None if not found
        """

        return session.get(Contact, contact_id)

    @session
    def get_or_create_contact(
        self,
        email: str,
        session: Session,
        name: str | None = None,
    ) -> Contact:
        if not email:
            raise ValueError("Contact email is required")
        contact = session.exec(select(Contact).where(Contact.email_address == email)).first()
        if contact:
            return contact
        resolved_name = name or email
        contact = Contact(name=resolved_name, email_address=email, is_known=False)
        session.add(contact)
        return contact

    def get_user_contact(self, user: User) -> Contact:
        return cast(Contact, self.get_or_create_contact(user.email, name=user.name or user.email))
