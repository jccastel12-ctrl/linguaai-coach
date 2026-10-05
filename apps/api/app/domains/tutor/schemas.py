import uuid
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from app.core.constants import CefrLevel

TutorPersonality = Literal["friendly", "patient", "professional"]
TurnRole = Literal["user", "assistant"]
MemoryCategory = Literal["grammar", "vocabulary", "pronunciation", "usage"]


class TutorSessionCreate(BaseModel):
    target_language_code: str = Field(min_length=2, max_length=8)
    cefr_level: CefrLevel = "A1"
    personality: TutorPersonality = "patient"


class TutorTurnRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    role: TurnRole
    content: str
    corrected_text: str | None
    explanation: str | None
    translation: str | None
    created_at: datetime


class TutorSessionRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    target_language_code: str
    cefr_level: CefrLevel
    personality: TutorPersonality
    title: str | None
    created_at: datetime
    updated_at: datetime


class TutorSessionDetail(TutorSessionRead):
    turns: list[TutorTurnRead] = []


class TutorMessageRequest(BaseModel):
    text: str = Field(min_length=1, max_length=2000)


class TutorExchange(BaseModel):
    session_id: uuid.UUID
    user_turn: TutorTurnRead
    assistant_turn: TutorTurnRead


class LearningMemoryRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    language_code: str
    category: MemoryCategory
    memory_key: str
    note: str
    occurrence_count: int
    last_example: str | None
    updated_at: datetime


class TutorStatsRead(BaseModel):
    total_sessions: int
    total_user_messages: int
    total_corrections: int
    memory_patterns: int
    repeated_patterns: int
    sessions_last_7_days: int
    most_frequent_category: MemoryCategory | None = None
    most_frequent_pattern: str | None = None
