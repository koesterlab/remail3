"""Fixtures for conversations, contacts, and users."""

from faker import Faker
from sqlmodel import Session

from remail.enums import ContactType, ConversationType, Protocol
from remail.models import Contact, Conversation, ConversationContact, User, UserConversation

fake = Faker()


def load_conversation_fixtures(
    session: Session, num_users: int = 3, num_contacts: int = 10
) -> None:
    """
    Load sample conversation fixtures into the database.

    Args:
        session: SQLModel database session
        num_users: Number of users to create (default: 3)
        num_contacts: Number of contacts to create (default: 10)
    """
    print("\n" + "=" * 80)
    print("Loading Conversation Fixtures")
    print("=" * 80 + "\n")

    # Create users
    users = []
    print(f"Creating {num_users} users...")
    for _ in range(num_users):
        user = User(
            name=fake.user_name(),
            email=fake.email(),
            password=fake.password(),
            protocol=Protocol.IMAP,
        )
        session.add(user)
        users.append(user)
    session.commit()
    print(f"✅ Created {len(users)} users\n")

    # Create contacts with varied types
    contacts = []
    contact_types = [
        ContactType.PRIVATE,
        ContactType.BUSINESS,
        ContactType.COMPANY,
        ContactType.NEWSLETTER,
    ]
    print(f"Creating {num_contacts} contacts...")
    for i in range(num_contacts):
        contact = Contact(
            name=fake.name(),
            email_address=fake.email(),
            first_name=fake.first_name(),
            last_name=fake.last_name(),
            contact_type=contact_types[i % len(contact_types)],
            is_known=fake.boolean(chance_of_getting_true=80),
        )
        session.add(contact)
        contacts.append(contact)
    session.commit()
    print(f"✅ Created {len(contacts)} contacts\n")

    # Create conversations
    conversations = []
    print("Creating conversations...")

    # 1. One-on-one conversations (CONVERSATION type)
    for i in range(min(5, len(contacts))):
        conv = Conversation(
            custom_name=f"{contacts[i].name}" if fake.boolean(chance_of_getting_true=70) else None,
            type=ConversationType.CONVERSATION,
        )
        session.add(conv)
        conversations.append(conv)

    # 2. Group conversations (GROUP type)
    for _ in range(3):
        conv = Conversation(
            custom_name=fake.catch_phrase() if fake.boolean(chance_of_getting_true=80) else None,
            type=ConversationType.GROUP,
        )
        session.add(conv)
        conversations.append(conv)

    session.commit()
    print(f"✅ Created {len(conversations)} conversations\n")

    # Link contacts to conversations
    print("Linking contacts to conversations...")
    link_count = 0
    for _i, conv in enumerate(conversations):
        if conv.type == ConversationType.CONVERSATION:
            # One-on-one: 1-2 contacts
            num_contacts_to_link = fake.random_int(min=1, max=2)
        else:
            # Group: 3-5 contacts
            num_contacts_to_link = fake.random_int(min=3, max=5)

        selected_contacts = fake.random_elements(
            elements=contacts, length=min(num_contacts_to_link, len(contacts)), unique=True
        )

        for contact in selected_contacts:
            conv_contact = ConversationContact(
                conversation_id=conv.id,
                contact_id=contact.id,
            )
            session.add(conv_contact)
            link_count += 1

    session.commit()
    print(f"✅ Created {link_count} conversation-contact links\n")

    # Link users to conversations with favorite status
    print("Linking users to conversations...")
    user_conv_count = 0
    for user in users:
        # Each user gets access to a random subset of conversations
        num_convs = fake.random_int(min=3, max=len(conversations))
        selected_convs = fake.random_elements(elements=conversations, length=num_convs, unique=True)

        for conv in selected_convs:
            user_conv = UserConversation(
                user_id=user.id,
                conversation_id=conv.id,
                is_favorite=fake.boolean(chance_of_getting_true=30),  # 30% chance of being favorite
            )
            session.add(user_conv)
            user_conv_count += 1

    session.commit()
    print(f"✅ Created {user_conv_count} user-conversation links\n")

    # Print summary
    print("=" * 80)
    print("Fixture Summary:")
    print("=" * 80)
    print(f"  Users:                    {len(users)}")
    print(f"  Contacts:                 {len(contacts)}")
    print(f"  Conversations:            {len(conversations)}")
    print(
        f"    - One-on-one:           {sum(1 for c in conversations if c.type == ConversationType.CONVERSATION)}"
    )
    print(
        f"    - Groups:               {sum(1 for c in conversations if c.type == ConversationType.GROUP)}"
    )
    print(f"  Conversation-Contact:     {link_count}")
    print(f"  User-Conversation:        {user_conv_count}")
    print(
        f"  Favorites:                {sum(1 for uc in session.query(UserConversation).all() if uc.is_favorite)}"
    )
    print("=" * 80 + "\n")
