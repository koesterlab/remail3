from remail.controllers.dtos.conversations import ContactDTO, ThreadPreviewDTO
from remail.controllers.dtos.threads import MessageDTO, ThreadDTO
from remail.enums import ContactType


# chatgpt
def fetch_thread(preview: ThreadPreviewDTO) -> ThreadDTO:
    contact = ContactDTO(
        id=2,
        first_name="John",
        last_name="Doe",
        email="john.doe@example.com",
        is_known=True,
        type=ContactType.PRIVATE,
    )

    me = ContactDTO(
        id=1,
        first_name="Me",
        last_name="User",
        email="me@example.com",
        is_known=True,
        type=ContactType.PRIVATE,
    )

    # Basisnachrichten
    messages = [
        MessageDTO(
            id=101,
            sender=contact,
            subject="Meeting Reminder",
            content="Hello, how are you?",
            sent_at="2024-05-30T10:15:30Z",
        ),
        MessageDTO(
            id=102,
            sender=me,
            subject="Re: Meeting Reminder",
            content="I'm good, thanks for asking!",
            sent_at="2024-05-30T10:17:45Z",
        ),
    ]

    # 15 zusätzliche Nachrichten
    additional_contents = [
        "Did you review the project proposal?",
        "Yes, looks good overall. A few changes needed.",
        "Which parts do you think need updates?",
        "The timeline section is a bit unclear.",
        "Alright, I'll revise it tonight.",
        "Perfect, let me know when it's done.",
        "The update is ready, please check again.",
        "Thanks! Reviewing it now.",
        "Looks much clearer. Nice work!",
        "Great! Should we schedule another meeting?",
        "Yes, how about tomorrow at 2 PM?",
        "That works for me.",
        "Sending out the meeting invite now.",
        "Got it, thank you!",
        "Looking forward to the meeting.",
    ]

    msg_id = 103
    sender_toggle = True

    for text in additional_contents:
        messages.append(
            MessageDTO(
                id=msg_id,
                sender=me if sender_toggle else contact,
                subject="Project Discussion",
                content=text,
                sent_at=f"2024-05-30T10:{20 + msg_id % 40:02d}:00Z",
            )
        )
        msg_id += 1
        sender_toggle = not sender_toggle

    # ---------------------------------------------------------
    # ThreadPreview + ThreadDTO
    # ---------------------------------------------------------

    return ThreadDTO(
        thread_id=preview.thread_id,
        title=preview.title,
        total_count=preview.total_count,
        unread_count=preview.unread_count,
        last_message=preview.last_message,
        last_message_datetime=preview.last_message_datetime,
        messages=messages,
    )
