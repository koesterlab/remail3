from sqlmodel import Session, select

from remail.interfaces.email.services.tagging_service import TaggingService
from remail.interfaces.llm.localLLMService import LocalLLM
from remail.models.email import Email
from remail.models.tag import Tag
from remail.models.tag_email import EmailTag
from remail.utils.session_management import session


class TaggingController:

    def __init__(self, llm: LocalLLM) -> None:
        self._service = TaggingService(llm)

    @session
    def get_tags(self, session: Session) -> list[Tag]:
        return list(session.exec(select(Tag)).all())

    @session
    def create_tag(self, name: str, description: str | None = None, *, session: Session) -> Tag:
        tag = Tag(name=name, description=description)
        session.add(tag)
        session.flush()
        return tag

    @session
    def delete_tag(self, tag_id: int, *, session: Session) -> None:
        tag = session.get(Tag, tag_id)
        if tag:
            session.delete(tag)

    @session
    def tag_email(self, email_id: int, *, session: Session) -> list[str]:
        email = session.get(Email, email_id)
        if email is None:
            raise ValueError(f"Email {email_id} not found")

        all_tags = list(session.exec(select(Tag)).all())
        if not all_tags:
            return []

        tags_dict = {t.name: (t.description or "") for t in all_tags}
        assigned_names = self._service.get_tags_for_email(email.body, tags_dict)

        name_to_tag = {t.name: t for t in all_tags}

        existing = session.exec(
            select(EmailTag).where(EmailTag.email_id == email_id)
        ).all()
        for link in existing:
            session.delete(link)
        for name in assigned_names:
            if tag := name_to_tag.get(name):
                session.add(EmailTag(tag_id=tag.id, email_id=email_id))

        return assigned_names

    @session
    def get_thread_tags(self, thread_id: int, *, session: Session) -> list[str]:
        emails = session.exec(
            select(Email).where(Email.thread_id == thread_id)
        ).all()
        seen: dict[int, str] = {}
        for email in emails:
            for tag in email.tags:
                seen[tag.id] = tag.name
        return list(seen.values())