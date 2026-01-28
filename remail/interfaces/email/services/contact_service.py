from sqlmodel import Session

from remail.database import engine
from remail.models import Contact


class ContactService:
    """Service for managing contacts."""

    def __init__(self) -> None:
        """Initialize contact service."""

        self.engine = engine

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
