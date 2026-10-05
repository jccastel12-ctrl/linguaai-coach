import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from app.core.constants import CefrLevel, ProgressStatus


class LessonSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    language_code: str
    slug: str
    title: str
    description: str | None
    cefr_level: CefrLevel
    order_index: int
    estimated_minutes: int


class LessonRead(LessonSummary):
    content: dict[str, Any]


class LessonProgressUpdate(BaseModel):
    status: ProgressStatus
    score: int | None = Field(default=None, ge=0, le=100)


class LessonProgressRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    lesson_id: uuid.UUID
    status: ProgressStatus
    score: int | None
    completed_at: datetime | None
