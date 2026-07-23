"""Data model for a single tracked background task."""

from dataclasses import dataclass


@dataclass
class TaskProgress:
    """Represents one running background task shown in the task tray.

    Attributes:
        task_id: Unique identifier chosen by the caller (e.g. ``"sync-user@example.com"``).
            Used to update or remove the task later.
        message: Human-readable description of what is currently happening.
            Displayed verbatim in the task tray.
        progress: Completion fraction in the range ``[0.0, 1.0]``, or ``None`` when the
            duration is unknown (renders as an indeterminate spinner instead of a bar).
    """

    task_id: str
    message: str
    progress: float | None = None
