from sqlmodel import Session, SQLModel, select

from remail.database import engine
from remail.models import Tag
from remail.utils.session_management import session

DEFAULT_TAGS = [
    ("Work", "Work or study related emails"),
    ("Personal", "Personal emails"),
    ("Urgent", "Emails that need quick attention"),
    ("Newsletter", "Newsletter or marketing emails"),
    ("Finance", "Invoices, payments, and banking"),
]


class TagService:
    def __init__(self) -> None:
        SQLModel.metadata.create_all(engine, tables=[Tag.__table__])  # type: ignore[attr-defined]

    @session
    def seed_default_tags(self, session: Session) -> None:
        if session.exec(select(Tag)).first() is not None:
            return
        for name, description in DEFAULT_TAGS:
            session.add(Tag(name=name, description=description))

    @session
    def get_all_tags(self, session: Session) -> list[Tag]:
        self.seed_default_tags(session=session)
        tags = list(session.exec(select(Tag).order_by(Tag.name)).all())
        for tag in tags:
            session.expunge(tag)
        return tags

    @session
    def create_tag(self, name: str, description: str = "", session: Session | None = None) -> Tag:
        if session is None:
            raise RuntimeError("TagService.create_tag requires a database session")
        clean_name = name.strip()
        if not clean_name:
            raise ValueError("Tag name cannot be empty")

        existing = session.exec(select(Tag).where(Tag.name == clean_name)).first()
        if existing:
            session.expunge(existing)
            return existing

        tag = Tag(name=clean_name, description=description.strip())
        session.add(tag)
        session.commit()
        session.refresh(tag)
        session.expunge(tag)
        return tag

    @session
    def delete_tag(self, tag_id: int, session: Session) -> None:
        tag = session.get(Tag, tag_id)
        if tag:
            session.delete(tag)
