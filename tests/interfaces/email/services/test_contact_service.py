"""Tests for ContactService."""

import pytest
from sqlmodel import Session, select

from remail.enums import ContactType, Protocol
from remail.interfaces.email.services.contact_service import ContactService
from remail.models import Contact, Conversation, ConversationContact, User, UserConversation


@pytest.fixture
def service(test_engine):
    """Create a ContactService instance with test engine."""
    svc = ContactService()
    svc.engine = test_engine
    return svc


def _create_user(session: Session, email: str) -> User:
    user = User(
        name=email.split("@")[0],
        email=email,
        host="imap.example.com",
        password="hash",
        protocol=Protocol.IMAP,
    )
    session.add(user)
    session.flush()
    return user


def _create_contact(
    session: Session,
    email: str,
    first_name: str = "First",
    last_name: str = "Last",
    contact_type: ContactType = ContactType.PRIVATE,
) -> Contact:
    contact = Contact(
        name=f"{first_name} {last_name}".strip(),
        email_address=email,
        first_name=first_name,
        last_name=last_name,
        contact_type=contact_type,
        is_known=True,
    )
    session.add(contact)
    session.flush()
    return contact


class TestContactService:
    """Test suite for ContactService."""

    def test_get_all_contacts_filters_by_user(self, service: ContactService, test_engine):
        """Test that contacts are scoped to the user's conversations."""
        with Session(test_engine) as session:
            user1 = _create_user(session, "user1@example.com")
            user2 = _create_user(session, "user2@example.com")

            contact1 = _create_contact(session, "contact1@example.com", "Alice", "One")
            contact2 = _create_contact(session, "contact2@example.com", "Bob", "Two")
            contact3 = _create_contact(session, "contact3@example.com", "Cara", "Three")

            conv1 = Conversation()
            conv2 = Conversation()
            session.add_all([conv1, conv2])
            session.flush()

            session.add_all(
                [
                    ConversationContact(
                        conversation_id=conv1.id,
                        contact_id=contact1.id,  # type: ignore[arg-type]
                    ),
                    ConversationContact(
                        conversation_id=conv1.id,
                        contact_id=contact2.id,  # type: ignore[arg-type]
                    ),
                    ConversationContact(
                        conversation_id=conv2.id,
                        contact_id=contact1.id,  # type: ignore[arg-type]
                    ),
                    ConversationContact(
                        conversation_id=conv2.id,
                        contact_id=contact3.id,  # type: ignore[arg-type]
                    ),
                ]
            )

            session.add_all(
                [
                    UserConversation(user_id=user1.id, conversation_id=conv1.id, is_favorite=False),
                    UserConversation(user_id=user1.id, conversation_id=conv2.id, is_favorite=False),
                    UserConversation(user_id=user2.id, conversation_id=conv2.id, is_favorite=False),
                ]
            )
            session.commit()

            user1_id = user1.id
            user2_id = user2.id

        result_user1 = service.get_all_contacts(user1_id)
        result_user2 = service.get_all_contacts(user2_id)

        assert {c.email_address for c in result_user1} == {
            "contact1@example.com",
            "contact2@example.com",
            "contact3@example.com",
        }
        assert len(result_user1) == 3
        assert {c.email_address for c in result_user2} == {
            "contact1@example.com",
            "contact3@example.com",
        }

    def test_create_contact_returns_none_for_blank_email(self, service: ContactService):
        """Test that create_contact returns None for empty emails."""
        result = service.create_contact(email="   ")
        assert result is None

    def test_create_contact_creates_new_contact(self, service: ContactService, test_engine):
        """Test creating a new contact persists and normalizes fields."""
        contact = service.create_contact(
            email="New@Example.com",
            first_name="New",
            last_name="Person",
            contact_type=ContactType.BUSINESS,
            is_known=False,
        )

        assert contact is not None
        assert contact.email_address == "new@example.com"
        assert contact.name == "New Person"
        assert contact.contact_type == ContactType.BUSINESS
        assert contact.is_known is False

        with Session(test_engine) as session:
            stored = session.exec(
                select(Contact).where(Contact.email_address == "new@example.com")
            ).first()
            assert stored is not None
            assert stored.id == contact.id

    def test_create_contact_returns_existing_contact(self, service: ContactService, test_engine):
        """Test that create_contact returns existing contact for same email."""
        with Session(test_engine) as session:
            existing = Contact(name="Existing", email_address="existing@example.com")
            session.add(existing)
            session.commit()
            session.refresh(existing)
            existing_id = existing.id

        contact = service.create_contact(email="existing@example.com")

        assert contact is not None
        assert contact.id == existing_id

        with Session(test_engine) as session:
            contacts = session.exec(select(Contact)).all()
            assert len(list(contacts)) == 1

    def test_create_contact_parses_name_when_missing_first_last(
        self, service: ContactService, test_engine
    ):
        """Test that name parsing sets first and last name."""
        contact = service.create_contact(
            email="jane@example.com",
            name="Jane Doe",
        )

        assert contact is not None
        assert contact.name == "Jane Doe"
        assert contact.first_name == "Jane"
        assert contact.last_name == "Doe"

        with Session(test_engine) as session:
            stored = session.exec(
                select(Contact).where(Contact.email_address == "jane@example.com")
            ).first()
            assert stored is not None
            assert stored.first_name == "Jane"
            assert stored.last_name == "Doe"
