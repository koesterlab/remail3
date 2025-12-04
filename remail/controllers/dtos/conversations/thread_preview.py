from dataclasses import dataclass
from datetime import datetime


@dataclass
class ThreadPreviewDTO:
    thread_id: int
    title: str
    total_count: int
    unread_count: int
    last_message: str
    last_message_datetime: datetime
