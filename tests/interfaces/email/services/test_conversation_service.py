"""Tests for ConversationService."""

import pytest
from sqlmodel import Session, select

from remail.enums import ContactType, ConversationType, Protocol
from remail.interfaces.email.services.conversation_service import ConversationService
from remail.models import Contact, Conversation, User


def _create_user(session: Session, email: str) -> User:
    user = User(
        name=email.split("@")[0],
        email=email,
        protocol=Protocol.IMAP,
        connection='{"host": "imap.example.com"}',
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


class TestConversationService:
    """Test suite for ConversationService."""

    @pytest.fixture
    def service(self, test_engine):
        svc = ConversationService()
        svc.engine = test_engine
        return svc

    @pytest.fixture
    def user_with_conversations(self, test_engine):
        with Session(test_engine) as session:
            user = _create_user(session, "test@example.com")
            contact1 = _create_contact(session, "contact1@example.com", "John", "Doe")
            contact2 = _create_contact(session, "contact2@example.com", "Jane", "Smith")

            conv1 = Conversation(
                custom_name="First Conversation",
                type=ConversationType.CONVERSATION,
                is_favorite=True,
            )
            conv2 = Conversation(
                custom_name="Second Conversation",
                type=ConversationType.GROUP,
                is_favorite=False,
            )
            session.add_all([conv1, conv2])
            session.flush()
            conv1.contacts.append(contact1)
            conv2.contacts.append(contact2)
            user.conversations.append(conv1)
            user.conversations.append(conv2)
            session.commit()
            return user.id

    def test_get_conversation_by_id_returns_conversation(self, service, test_engine):
        """Test get_conversation_by_id returns Conversation model."""
        with Session(test_engine) as session:
            user = _create_user(session, "user@example.com")
            contact = _create_contact(session, "contact@example.com")
            conversation = Conversation(custom_name="Single", type=ConversationType.CONVERSATION, user=user)
            session.add(conversation)
            session.flush()
            conversation.contacts.append(contact)
            session.commit()
            conversation_id = conversation.id

        result = service.get_conversation_by_id(conversation_id)
        assert result is not None
        assert isinstance(result, Conversation)
        assert result.custom_name == "Single"
        assert len(result.contacts) == 1
        assert result.contacts[0].email_address == "contact@example.com"

    def test_get_conversation_by_id_raises_when_not_found(self, service):
        """Test get_conversation_by_id raises ValueError when conversation not found."""
        with pytest.raises(ValueError, match="Conversation with id 99999 not found"):
            service.get_conversation_by_id(99999)

    def test_create_conversation_creates_group_conversation(self, service, test_engine):
        with Session(test_engine) as session:
            user = _create_user(session, "group@example.com")
            contact1 = _create_contact(session, "alice@example.com", "Alice", "One")
            contact2 = _create_contact(session, "bob@example.com", "Bob", "Two")
            session.commit()
            result = service.create_conversation(
                conversation_type=ConversationType.GROUP,
                contacts=[contact1, contact2],
                custom_name="Team",
                user=user,
                session=session,
            )
            session.commit()
            session.refresh(result)
            assert len(result.contacts) == 2
            conversation_id = result.id

        assert result is not None
        assert result.custom_name == "Team"
        assert result.type == ConversationType.GROUP

        with Session(test_engine) as session:
            conversation = session.exec(
                select(Conversation).where(Conversation.id == conversation_id)
            ).first()
            assert conversation is not None
            assert len(conversation.contacts) == 2

    def test_get_conversation_by_members_finds_match(self, service, test_engine):
        with Session(test_engine) as session:
            user = _create_user(session, "members@example.com")
            contact = _create_contact(session, "member@example.com")
            conversation = Conversation(custom_name="Members", type=ConversationType.CONVERSATION)
            session.add(conversation)
            session.flush()
            conversation.contacts.append(contact)
            user.conversations.append(conversation)
            session.commit()

            contact_id = contact.id

        with Session(test_engine) as session:
            contact = session.exec(select(Contact).where(Contact.id == contact_id)).first()

        with Session(test_engine) as session:
            result = service.get_conversation_by_members([contact], session=session)
        assert result is not None
        assert result.custom_name == "Members"

    def test_get_conversation_by_members_returns_none_for_missing_ids(self, service):
        ghost = Contact(name="Ghost", email_address="ghost@example.com")
        result = service.get_conversation_by_members([ghost])
        assert result is None
