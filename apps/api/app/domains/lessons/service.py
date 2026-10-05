import uuid
from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domains.lessons.models import Lesson, LessonProgress
from app.domains.lessons.schemas import LessonProgressUpdate


async def list_lessons(
    db: AsyncSession,
    *,
    language_code: str | None = None,
    cefr_level: str | None = None,
    limit: int = 50,
    offset: int = 0,
) -> list[Lesson]:
    stmt = select(Lesson).where(Lesson.is_published.is_(True))
    if language_code:
        stmt = stmt.where(Lesson.language_code == language_code.lower())
    if cefr_level:
        stmt = stmt.where(Lesson.cefr_level == cefr_level)
    stmt = stmt.order_by(Lesson.language_code, Lesson.cefr_level, Lesson.order_index).limit(limit).offset(offset)
    return list(await db.scalars(stmt))


async def get_published_lesson(db: AsyncSession, lesson_id: uuid.UUID) -> Lesson | None:
    lesson = await db.get(Lesson, lesson_id)
    return lesson if lesson and lesson.is_published else None


async def list_progress(db: AsyncSession, user_id: uuid.UUID) -> list[LessonProgress]:
    return list(await db.scalars(select(LessonProgress).where(LessonProgress.user_id == user_id)))


async def upsert_progress(
    db: AsyncSession, user_id: uuid.UUID, lesson_id: uuid.UUID, data: LessonProgressUpdate
) -> LessonProgress:
    progress = await db.scalar(
        select(LessonProgress).where(LessonProgress.user_id == user_id, LessonProgress.lesson_id == lesson_id)
    )
    if progress is None:
        progress = LessonProgress(user_id=user_id, lesson_id=lesson_id)
        db.add(progress)
    progress.status = data.status
    progress.score = data.score
    progress.completed_at = datetime.now(UTC) if data.status == "completed" else None
    await db.commit()
    await db.refresh(progress)
    return progress
