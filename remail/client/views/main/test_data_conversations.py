from remail.controllers.dtos.conversations import ConversationDTO, ThreadPreviewDTO, ContactDTO
from datetime import datetime, timedelta
from typing import List
import random
from remail.enums import ContactType


def create_test_data(): #chatgpt
    first_names = ["Alice", "Bob", "Charlie", "Diana", "Eve", "Frank", "Grace", "Hannah", "Ivan", "Judy"]
    last_names = ["Smith", "Johnson", "Brown", "Miller", "Davis", "Wilson", "Taylor", "Anderson", "Thomas", "Jackson"]
    messages = [
        "Hey, wie geht's?", "Treffen wir uns morgen?", "Hast du die Unterlagen?",
        "Danke!", "Klingt gut!", "Ich melde mich später.", "Alles klar!", "Lass uns telefonieren."
    ]

    conversations: List[ConversationDTO] = []

    contact_id_counter = 1
    thread_id_counter = 1

    for i in range(17):
        # Zufällige Anzahl von Kontakten: 1 für Einzelchat, 2-4 für Gruppen
        if i < 5:
            num_contacts = 1
        else:
            num_contacts = random.randint(2, 4)

        contacts = []
        for _ in range(num_contacts):
            contacts.append(ContactDTO(
                id=contact_id_counter,
                first_name=random.choice(first_names),
                last_name=random.choice(last_names),
                email=f"user{contact_id_counter}@example.com",
                is_known=random.choice([True, False]),
                type=ContactType.PRIVATE
            ))
            contact_id_counter += 1

        # Threads: 2-5 pro Conversation
        threads = []
        for _ in range(random.randint(2, 5)):
            threads.append(ThreadPreviewDTO(
                thread_id=thread_id_counter,
                title=f"Thread {thread_id_counter}",
                total_count=random.randint(5, 50),
                unread_count=random.randint(0, 10),
                last_message=random.choice(messages),
                last_message_datetime=datetime.now() - timedelta(days=random.randint(0, 30))
            ))
            thread_id_counter += 1

        conversations.append(ConversationDTO(
            contacts=contacts,
            threads=threads,
            is_favorite=random.choice([True, False]),
            customName=None if num_contacts == 1 else f"Gruppe {i + 1}"
        ))
    return conversations

def create_search_result_test_data(term: str):
    return [ConversationDTO(
        contacts=[ContactDTO(
                id=1,
                first_name="Gandalf",
                last_name=term,
                email=f"user@example.com",
                is_known=False,
                type=ContactType.PRIVATE
            )],
        threads=[ThreadPreviewDTO(
            thread_id=1,
            title=f"Thread 1",
            total_count=random.randint(5, 50),
            unread_count=random.randint(0, 10),
            last_message="random.choice(messages)",
            last_message_datetime=datetime.now() - timedelta(days=random.randint(0, 30))
        )],
        is_favorite=random.choice([True, False]),
        customName=None
    ),ConversationDTO(
        contacts=[ContactDTO(
                id=1,
                first_name="Manfred",
                last_name="Manfred",
                email=f"manfred@example.com",
                is_known=False,
                type=ContactType.PRIVATE
            )],
        threads=[ThreadPreviewDTO(
            thread_id=1,
            title=f"Thread 1",
            total_count=random.randint(5, 50),
            unread_count=random.randint(0, 10),
            last_message="random.choice(messages)",
            last_message_datetime=datetime.now() - timedelta(days=random.randint(0, 30))
        )],
        is_favorite=random.choice([True, False]),
        customName=None
    )]

