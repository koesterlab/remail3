"""Service for managing email tags."""

from __future__ import annotations

from sqlalchemy import func
from sqlmodel import Session, SQLModel, select

import remail.database as database
from remail.models import Email, EmailTag, Tag
from remail.utils.session_management import session

DEFAULT_TAGS: tuple[tuple[str, str], ...] = (
    ("Work", "Professional messages, meetings, and tasks"),
    ("Personal", "Friends, family, and private messages"),
    ("Urgent", "Messages that need quick attention"),
    ("Newsletter", "Mailing lists and recurring updates"),
    ("Finance", "Invoices, bills, and banking"),
)


class TagService:
    """Database operations for tag definitions and email-tag links."""

    def __init__(self) -> None:
        SQLModel.metadata.create_all(database.engine)

    @session
    def seed_default_tags(self, session: Session) -> None:
        """Insert starter tags when the tag table is empty."""
        existing_count = session.exec(select(func.count()).select_from(Tag)).one()
        if existing_count:
            return
        for name, description in DEFAULT_TAGS:
            session.add(Tag(name=name, description=description))

    @session
    def get_all_tags(self, session: Session) -> list[Tag]:
        self.seed_default_tags()
        session.expire_on_commit = False
        return list(session.exec(select(Tag).order_by(Tag.name)).all())

    @session
    def create_tag(self, name: str, description: str | None, session: Session) -> Tag:
        normalized_name = name.strip()
        normalized_description = description.strip() if description else None
        if not normalized_name:
            raise ValueError("Tag name must not be empty.")

        session.expire_on_commit = False
        existing = session.exec(select(Tag).where(Tag.name == normalized_name)).first()
        if existing:
            return existing

        tag = Tag(name=normalized_name, description=normalized_description)
        session.add(tag)
        session.flush()
        session.refresh(tag)
        return tag

    @session
    def delete_tag(self, tag_id: int, session: Session) -> None:
        links = session.exec(select(EmailTag).where(EmailTag.tag_id == tag_id)).all()
        for link in links:
            session.delete(link)
        tag = session.get(Tag, tag_id)
        if tag:
            session.delete(tag)

    @session
    def get_tags_for_thread(self, thread_id: int, session: Session) -> list[Tag]:
        session.expire_on_commit = False
        rows = session.exec(
            select(Tag)
            .join(EmailTag, EmailTag.tag_id == Tag.id)
            .join(Email, Email.id == EmailTag.email_id)
            .where(Email.thread_id == thread_id)
            .order_by(Tag.name)
        ).all()
        seen: dict[int, Tag] = {}
        for tag in rows:
            if tag.id is not None:
                seen[tag.id] = tag
        return list(seen.values())

    @session
    def add_tag_to_thread(self, thread_id: int, tag_id: int, session: Session) -> None:
        tag = session.get(Tag, tag_id)
        if tag is None:
            raise ValueError(f"Tag {tag_id} not found.")

        emails = session.exec(select(Email).where(Email.thread_id == thread_id)).all()
        for email in emails:
            if email.id is None:
                continue
            existing = session.exec(
                select(EmailTag).where(
                    EmailTag.email_id == email.id,
                    EmailTag.tag_id == tag_id,
                )
            ).first()
            if existing is None:
                session.add(EmailTag(email_id=email.id, tag_id=tag_id))

    @session
    def remove_tag_from_thread(self, thread_id: int, tag_id: int, session: Session) -> None:
        emails = session.exec(select(Email).where(Email.thread_id == thread_id)).all()
        email_ids = [email.id for email in emails if email.id is not None]
        for email_id in email_ids:
            link = session.exec(
                select(EmailTag).where(
                    EmailTag.email_id == email_id,
                    EmailTag.tag_id == tag_id,
                )
            ).first()
            if link:
                session.delete(link)
