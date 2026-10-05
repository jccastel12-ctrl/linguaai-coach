import uuid
from typing import Annotated

from fastapi import APIRouter, HTTPException, Query, status

from app.core.constants import CefrLevel
from app.domains.auth.dependencies import CurrentUser, DbSession
from app.domains.lessons import service
from app.domains.lessons.schemas import LessonProgressRead, LessonProgressUpdate, LessonRead, LessonSummary

router = APIRouter(prefix="/lessons", tags=["lessons"])


@router.get("", response_model=list[LessonSummary])
async def list_lessons(
    db: DbSession,
    language: Annotated[str | None, Query(min_length=2, max_length=8)] = None,
    level: CefrLevel | None = None,
    limit: Annotated[int, Query(ge=1, le=100)] = 50,
    offset: Annotated[int, Query(ge=0)] = 0,
):
    return await service.list_lessons(db, language_code=language, cefr_level=level, limit=limit, offset=offset)


@router.get("/progress/me", response_model=list[LessonProgressRead])
async def my_progress(current_user: CurrentUser, db: DbSession):
    return await service.list_progress(db, current_user.id)


@router.get("/{lesson_id}", response_model=LessonRead)
async def get_lesson(lesson_id: uuid.UUID, db: DbSession):
    lesson = await service.get_published_lesson(db, lesson_id)
    if lesson is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Lesson not found")
    return lesson


@router.put("/{lesson_id}/progress", response_model=LessonProgressRead)
async def update_progress(lesson_id: uuid.UUID, data: LessonProgressUpdate, current_user: CurrentUser, db: DbSession):
    if await service.get_published_lesson(db, lesson_id) is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Lesson not found")
    return await service.upsert_progress(db, current_user.id, lesson_id, data)
