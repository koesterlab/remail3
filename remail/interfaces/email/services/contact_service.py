from typing import cast

from sqlmodel import Session, col, select

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

    @session
    def get_or_create_contacts_batch(
        self,
        emails_names: list[tuple[str, str | None]],
        session: Session,
    ) -> dict[str, Contact]:
        emails = [e for e, _ in emails_names if e]
        if not emails:
            return {}
        existing = {
            c.email_address: c
            for c in session.exec(select(Contact).where(col(Contact.email_address).in_(emails))).all()
        }
        for email, name in emails_names:
            if not email or email in existing:
                continue
            contact = Contact(name=name or email, email_address=email, is_known=False)
            session.add(contact)
            existing[email] = contact
        return existing
