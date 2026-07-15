import math

from sqlalchemy import inspect
from sqlmodel import Session, SQLModel, col, select

from remail import database
from remail.interfaces.embeddings.embedding_service import EmbeddingService
from remail.models import Email, EmailTag, Tag
from remail.utils.session_management import session

# Descriptions are embedded together with the name to anchor each tag in vector
# space, so keyword-dense wording directly improves auto-tagging accuracy.
DEFAULT_TAGS = [
    (
        "Work",
        "Job, projects and meetings: deadlines, sprints, reports, code reviews, colleagues, customers, appointments",
    ),
    (
        "Personal",
        "Private life with friends and family: invitations, birthdays, trips, photos, hobbies, pets, everyday plans",
    ),
    (
        "Urgent",
        "Time-critical, needs immediate action today: emergency, outage, deadline expiring, cancellation, call back now",
    ),
    (
        "Newsletter",
        "Newsletters and marketing mail: weekly digest, product news, sale, discount, promotion, subscription, unsubscribe",
    ),
    (
        "Spam",
        "System tag",
    ),
]

# Raw similarity scores are biased: each tag has its own baseline similarity to
# arbitrary text (e.g. "Work" sits close to everything), which drowns out the
# actual match. Scores are therefore calibrated by subtracting the tag's mean
# similarity to these neutral, topic-free snippets — a tag only wins when it
# matches this email more than it matches ordinary mail.
_NEUTRAL_TEXTS = [
    "Hello, I hope you are doing well.",
    "Thanks for your message, I will get back to you.",
    "Here is the information you asked about.",
    "Let me know what you think.",
    "See the details below.",
    "Hallo, ich hoffe es geht dir gut.",
    "Danke für deine Nachricht, ich melde mich bald.",
    "Viele Grüße und bis bald.",
    "Can you take a look at this when you have a moment?",
    "Just following up on my last message.",
]

# Thresholds apply to calibrated scores (raw minus baseline), which live on a
# small scale around zero: the best tag wins if it clears the floor, and other
# tags are only added when nearly tied with it.
_SCORE_FLOOR = 0.01
_SCORE_MARGIN = 0.005
_MAX_TAGS = 3

# Built-in tag decided by the mail server's spam (see EmailParser._is_spam).
SPAM_TAG_NAME = "Spam"

# Schema setup runs once per process; defaults are seeded only when the tags
# table is first created, so deleting them later doesn't resurrect them.
_schema_ready = False


def _cosine_similarity(a: list[float], b: list[float]) -> float:
    """
    Measure how similar two embedding vectors are by the angle between them.

    Computed as (a · b) / (|a| * |b|), i.e. the cosine of the angle between the
    vectors. The result ranges from -1 to 1: 1 means the vectors point in the
    same direction (texts mean nearly the same thing), 0 means they are
    unrelated, -1 opposite. Because it ignores vector length and only compares
    direction, a short tag description can still score high against a long
    email body. Zero vectors have no direction, so they score 0.
    """
    dot = sum(x * y for x, y in zip(a, b, strict=True))
    norm_a = math.sqrt(sum(x * x for x in a))
    norm_b = math.sqrt(sum(x * x for x in b))
    if norm_a == 0.0 or norm_b == 0.0:
        return 0.0
    return dot / (norm_a * norm_b)


class TagService:
    def __init__(self) -> None:
        # Built lazily so UI paths (settings, dashboard) never touch the embedding stack.
        self._embedding_service: EmbeddingService | None = None
        # Tag texts rarely change; keyed by the embedded text so edits invalidate naturally.
        self._tag_embedding_cache: dict[str, list[float]] = {}
        self._tag_baseline_cache: dict[str, float] = {}
        self._neutral_vectors: list[list[float]] | None = None
        self._ensure_schema()

    def _ensure_schema(self) -> None:
        global _schema_ready
        if _schema_ready:
            return
        tags_existed = inspect(database.engine).has_table("tags")
        SQLModel.metadata.create_all(
            database.engine,
            tables=[Tag.__table__, EmailTag.__table__],  # type: ignore[attr-defined]
        )
        if not tags_existed:
            with Session(database.engine) as seed_session:
                self.seed_default_tags(session=seed_session)
                seed_session.commit()
        _schema_ready = True

    @session
    def seed_default_tags(self, session: Session) -> None:
        if session.exec(select(Tag)).first() is not None:
            return
        for name, description in DEFAULT_TAGS:
            session.add(Tag(name=name, description=description))

    @session
    def get_all_tags(self, session: Session) -> list[Tag]:
        tags = list(session.exec(select(Tag).order_by(Tag.name)).all())
        for tag in tags:
            session.expunge(tag)
        return tags

    @session
    def create_tag(self, name: str, description: str = "", *, session: Session) -> Tag:
        clean_name = name.strip()
        if not clean_name:
            raise ValueError("Tag name cannot be empty")

        existing = session.exec(select(Tag).where(Tag.name == clean_name)).first()
        if existing:
            session.expunge(existing)
            return existing

        tag = Tag(name=clean_name, description=description.strip())
        session.add(tag)
        session.flush()
        session.expunge(tag)
        return tag

    @session
    def get_thread_tags(self, thread_id: int, session: Session) -> list[Tag]:
        """Return the union of tags assigned to all emails in a thread."""
        statement = (
            select(Tag)
            .join(EmailTag)
            .join(Email)
            .where(Email.thread_id == thread_id)
            .distinct()
            .order_by(Tag.name)
        )
        tags = list(session.exec(statement).all())
        for tag in tags:
            session.expunge(tag)
        return tags

    @session
    def set_email_tags(self, email_id: int, tag_names: list[str], session: Session) -> None:
        """Replace an email's tag assignments with the tags matching the given names."""
        for link in session.exec(select(EmailTag).where(EmailTag.email_id == email_id)).all():
            session.delete(link)
        if not tag_names:
            return
        tags = session.exec(select(Tag).where(col(Tag.name).in_(tag_names))).all()
        for tag in tags:
            if tag.id is not None:
                session.add(EmailTag(tag_id=tag.id, email_id=email_id))

    @session
    def delete_tag(self, tag_id: int, session: Session) -> None:
        tag = session.get(Tag, tag_id)
        if tag and tag.name.casefold() == "spam":
            raise ValueError("Spam is a built-in tag and cannot be deleted")
        for link in session.exec(select(EmailTag).where(EmailTag.tag_id == tag_id)).all():
            session.delete(link)
        if tag:
            session.delete(tag)

    # --- Automatic tagging (embedding similarity, runs in background threads) ---

    def auto_tag_email(
        self,
        email_id: int,
        chunk_vectors: list[list[float]] | None = None,
        subject: str = "",
        is_spam: bool = False,
    ) -> None:
        """
        Assign tags to an email. Designed to run in a background thread.

        Spam is decided by the mail server (see EmailParser._is_spam), not by
        embeddings: junk mail resembles many legitimate topics, so scoring it by
        similarity is unreliable. A spam-flagged email is tagged Spam and skips
        the embedding step; everything else is scored against the remaining tags,
        assuming it is not spam.

        Pass the email's stored chunk embeddings (from the search index) to avoid
        re-embedding the body; those already include the subject. Without them,
        subject and body are embedded as a fallback.
        """
        if is_spam:
            self.set_email_tags(email_id, [SPAM_TAG_NAME])
            return

        # Spam is server-decided, so exclude it from similarity scoring entirely.
        tags = [tag for tag in self.get_all_tags() if tag.name.casefold() != SPAM_TAG_NAME.casefold()]
        if not tags:
            return
        if not chunk_vectors:
            body = self._get_email_body(email_id)
            if body is None:
                return
            # Mirror the search index's subject enrichment (see SearchController.index_email).
            text = (f"Betreff: {subject}\n\n" if subject else "") + body[:2000]
            if not text.strip():
                return
            chunk_vectors = [self._get_embedding_service().get_embedding(text)]
        assigned = self.get_tags_for_email(chunk_vectors, tags)
        self.set_email_tags(email_id, assigned)

    def retag_all_emails(self) -> int:
        """
        Re-run automatic tagging for every non-deleted, non-spam email.

        Useful after tags were added or deleted, so existing mail reflects the new
        tag set. Reuses the chunk embeddings stored in the search index; emails not
        indexed yet fall back to embedding subject and body. Server-flagged spam is
        left untouched (see _get_taggable_emails). Designed to run in a background
        thread. Returns the number of emails processed.
        """
        # Imported lazily so UI paths never load the search/embedding stack.
        from remail.controllers.search_controller import SearchController

        search_controller = SearchController()
        emails = self._get_taggable_emails()
        for email_id, subject in emails:
            chunk_vectors = search_controller.get_chunk_embeddings(email_id)
            self.auto_tag_email(email_id, chunk_vectors=chunk_vectors, subject=subject)
        return len(emails)

    @session
    def _get_taggable_emails(self, session: Session) -> list[tuple[int, str]]:
        """
        Return (id, subject) of non-deleted emails to auto-tag, newest first.

        Server-flagged spam is excluded: spam is decided by the mail server and
        persisted only as the Spam tag, so re-scoring it by similarity would wrongly
        strip that classification.
        """
        spam_email_ids = (
            select(EmailTag.email_id)
            .join(Tag, col(EmailTag.tag_id) == col(Tag.id))
            .where(col(Tag.name).ilike(SPAM_TAG_NAME))
        )
        statement = (
            select(Email)
            .where(col(Email.deleted).is_(False))
            .where(col(Email.id).not_in(spam_email_ids))
            .order_by(col(Email.sent_at).desc())
        )
        emails = session.exec(statement).all()
        return [
            (email.id, email.thread.title if email.thread else "")
            for email in emails
            if email.id is not None
        ]

    @session
    def _get_email_body(self, email_id: int, session: Session) -> str | None:
        email = session.get(Email, email_id)
        return email.body if email else None

    def _get_embedding_service(self) -> EmbeddingService:
        if self._embedding_service is None:
            self._embedding_service = EmbeddingService()
        return self._embedding_service

    def _get_neutral_vectors(self) -> list[list[float]]:
        if self._neutral_vectors is None:
            embed = self._get_embedding_service().get_embedding
            self._neutral_vectors = [embed(text) for text in _NEUTRAL_TEXTS]
        return self._neutral_vectors

    def _get_tag_baseline(self, tag_text: str, tag_vec: list[float]) -> float:
        baseline = self._tag_baseline_cache.get(tag_text)
        if baseline is None:
            neutral = self._get_neutral_vectors()
            baseline = sum(_cosine_similarity(vec, tag_vec) for vec in neutral) / len(neutral)
            self._tag_baseline_cache[tag_text] = baseline
        return baseline

    def get_tags_for_email(self, chunk_vectors: list[list[float]], tags: list[Tag]) -> list[str]:
        """
        Return the best-matching tag names for the email.

        Each tag is scored as its best cosine similarity against any chunk, so a
        topic mentioned anywhere in a long email can still earn its tag. That raw
        score is calibrated by subtracting the tag's neutral-text baseline (see
        _NEUTRAL_TEXTS). The top-scoring tag is assigned if it clears
        _SCORE_FLOOR; further tags are assigned only when within _SCORE_MARGIN
        of the top score.
        """
        if not tags or not chunk_vectors:
            return []

        scored: list[tuple[str, float]] = []
        for tag in tags:
            tag_text = f"{tag.name}: {tag.description}" if tag.description else tag.name
            tag_vec = self._tag_embedding_cache.get(tag_text)
            if tag_vec is None:
                tag_vec = self._get_embedding_service().get_embedding(tag_text)
                self._tag_embedding_cache[tag_text] = tag_vec
            best = max(_cosine_similarity(chunk_vec, tag_vec) for chunk_vec in chunk_vectors)
            scored.append((tag.name, best - self._get_tag_baseline(tag_text, tag_vec)))

        scored.sort(key=lambda x: x[1], reverse=True)
        top_score = scored[0][1]
        if top_score < _SCORE_FLOOR:
            return []
        return [name for name, sim in scored[:_MAX_TAGS] if sim >= top_score - _SCORE_MARGIN]
