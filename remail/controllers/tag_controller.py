from remail.interfaces.email.services.tag_service import TagService
from remail.models import Tag


class TagController:
    def __init__(self) -> None:
        self.service = TagService()

    def get_all_tags(self) -> list[Tag]:
        return self.service.get_all_tags()

    def create_tag(self, name: str, description: str = "") -> Tag:
        return self.service.create_tag(name, description)

    def delete_tag(self, tag_id: int) -> None:
        self.service.delete_tag(tag_id)
