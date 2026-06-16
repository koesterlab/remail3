"""Controller for manual email tag operations."""

from __future__ import annotations

from remail.interfaces.email.services.tag_service import TagService
from remail.models import Tag


class TagController:
    """UI-facing wrapper around tag persistence."""

    def __init__(self) -> None:
        self.service = TagService()

    def get_all_tags(self) -> list[Tag]:
        return self.service.get_all_tags()

    def create_tag(self, name: str, description: str | None = None) -> Tag:
        return self.service.create_tag(name, description)

    def delete_tag(self, tag_id: int) -> None:
        self.service.delete_tag(tag_id)

    def get_tags_for_thread(self, thread_id: int) -> list[Tag]:
        return self.service.get_tags_for_thread(thread_id)

    def add_tag_to_thread(self, thread_id: int, tag_id: int) -> None:
        self.service.add_tag_to_thread(thread_id, tag_id)

    def remove_tag_from_thread(self, thread_id: int, tag_id: int) -> None:
        self.service.remove_tag_from_thread(thread_id, tag_id)
