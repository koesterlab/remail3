from datetime import datetime

from remail.controllers.dtos.conversations import ThreadPreviewDTO
from remail.controllers.dtos.threads import MessageContentDTO, MessageDTO, SenderDTO, ThreadDTO


# chatgpt
def fetch_thread(preview: ThreadPreviewDTO) -> ThreadDTO:
    contact = SenderDTO(
        id=2,
        first_name="John",
        last_name="Doe",
        email="john.doe@example.com",
    )

    me = SenderDTO(
        id=1,
        first_name="Me",
        last_name="User",
        email="me@example.com",
    )

    # Basisnachrichten
    messages = [
        MessageDTO(
            id=101,
            sender=contact,
            subject="Meeting Reminder",
            content=MessageContentDTO(body="Hello, how are you?", attachments=[]),
            sent_at=datetime(2024, 5, 30, 10, 15, 30),
        ),
        MessageDTO(
            id=102,
            sender=me,
            subject="Re: Meeting Reminder",
            content=MessageContentDTO(body="I'm good, thanks for asking!", attachments=[]),
            sent_at=datetime(2024, 5, 30, 10, 17, 45),
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
                content=MessageContentDTO(body=text, attachments=[]),
                sent_at=datetime(2024, 5, 30, 10, 20 + msg_id % 40, 0),
            )
        )
        msg_id += 1
        sender_toggle = not sender_toggle

    # ---------------------------------------------------------
    # ThreadDTO
    # ---------------------------------------------------------

    return ThreadDTO(
        id=preview.thread_id,
        title=preview.title,
        messages=messages,
    )
