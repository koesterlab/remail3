from remail.interfaces.email.services.tag_service import TagService
from remail.models import Tag


class TagController:
    def __init__(self) -> None:
        self.service = TagService()

    def get_all_tags(self) -> list[Tag]:
        return self.service.get_all_tags()  # type: ignore[no-any-return]

    def get_thread_tags(self, thread_id: int) -> list[Tag]:
        return self.service.get_thread_tags(thread_id)  # type: ignore[no-any-return]

    def create_tag(self, name: str, description: str = "") -> Tag:
        return self.service.create_tag(name, description)  # type: ignore[no-any-return]

    def delete_tag(self, tag_id: int) -> None:
        self.service.delete_tag(tag_id)

    def retag_all_emails(self) -> int:
        return self.service.retag_all_emails()
