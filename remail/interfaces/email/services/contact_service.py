from sqlmodel import Session

from remail.database import engine
from remail.models import Contact


class ContactService:
    def __init__(self):
        """
        Initialize conversation service.
        """

        self.engine = engine

    def get_contact_by_id(self, contact_id: int) -> Contact | None:
        """
        Fetch a contact by its ID.

        Args:
            contact_id: Contact ID to fetch

        Returns:
            Contact object if found, else None
        """
        with Session(self.engine) as session:
            contact = session.get(Contact, contact_id)

            return contact

    def create_contact(self, name: str, email: str) -> Contact:
        new_contact = Contact(
            name=name,
            email_address=email,
        )

        with Session(self.engine) as session:
            session.add(new_contact)
            session.commit()
            session.refresh(new_contact)

        return new_contact
