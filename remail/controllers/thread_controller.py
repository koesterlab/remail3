from remail.controllers.dtos.conversations import ConversationDTO
from remail.controllers.dtos.threads import ThreadDTO
from remail.controllers.dtos.user_dto import UserDTO
from remail.interfaces.email.services.thread_service import ThreadService


class ThreadController:
    """Controller for thread operations."""

    def __init__(self):
        """Initialize thread controller."""

        self.service = ThreadService()

    def get_thread(self, thread_id: int) -> ThreadDTO | None:
        """
        Fetch a complete thread with all messages.

        Args:
            thread_id: Thread ID to fetch

        Returns:
            ThreadDTO with thread data, or None if not found
        """

        result: ThreadDTO | None = self.service.get_thread_by_id(thread_id)

        return result

    def get_most_urgent_threads(
        self, count: int = 5
    ) -> list[tuple[ThreadDTO, ConversationDTO, UserDTO]]:
        return self.service.get_most_important_threads(count=count)  # type:ignore
