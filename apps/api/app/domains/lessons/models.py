import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import (
    JSON,
    Boolean,
    CheckConstraint,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
    Uuid,
    false,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.core.constants import CEFR_LEVELS, PROGRESS_STATUSES, sql_in
from app.core.database import Base, TimestampMixin


class Lesson(Base, TimestampMixin):
    __tablename__ = "lessons"
    __table_args__ = (
        UniqueConstraint("language_code", "slug", name="uq_lessons_language_slug"),
        CheckConstraint(f"cefr_level IN {sql_in(CEFR_LEVELS)}", name="cefr_level_valid"),
        CheckConstraint("estimated_minutes > 0", name="estimated_minutes_positive"),
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    language_code: Mapped[str] = mapped_column(
        ForeignKey("languages.code", ondelete="RESTRICT"), index=True, nullable=False
    )
    slug: Mapped[str] = mapped_column(String(120), nullable=False)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    cefr_level: Mapped[str] = mapped_column(String(2), nullable=False)
    order_index: Mapped[int] = mapped_column(Integer, default=0, server_default="0", nullable=False)
    estimated_minutes: Mapped[int] = mapped_column(Integer, default=10, server_default="10", nullable=False)
    # Structured lesson content (sections, vocabulary, exercises). Schema versioned inside the JSON.
    content: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)
    is_published: Mapped[bool] = mapped_column(Boolean, default=False, server_default=false(), nullable=False)


class LessonProgress(Base, TimestampMixin):
    __tablename__ = "lesson_progress"
    __table_args__ = (
        UniqueConstraint("user_id", "lesson_id", name="uq_lesson_progress_user_lesson"),
        CheckConstraint(f"status IN {sql_in(PROGRESS_STATUSES)}", name="status_valid"),
        CheckConstraint("score IS NULL OR (score BETWEEN 0 AND 100)", name="score_range"),
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    lesson_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("lessons.id", ondelete="CASCADE"), index=True, nullable=False
    )
    status: Mapped[str] = mapped_column(String(20), default="not_started", server_default="not_started", nullable=False)
    score: Mapped[int | None] = mapped_column(Integer)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
