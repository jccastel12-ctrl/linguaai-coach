import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.core.constants import CefrLevel


class PronunciationExercise(BaseModel):
    id: str
    language_code: str
    cefr_level: CefrLevel
    text: str
    focus_sound: str | None = None
    tip: str


class PronunciationEvaluateRequest(BaseModel):
    language_code: str = Field(min_length=2, max_length=8)
    cefr_level: CefrLevel
    expected_text: str = Field(min_length=1, max_length=500)
    recognized_text: str = Field(min_length=1, max_length=500)
    browser_confidence: float | None = Field(default=None, ge=0, le=1)
    focus_sound: str | None = Field(default=None, max_length=80)


class PronunciationEvaluation(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    language_code: str
    cefr_level: CefrLevel
    expected_text: str
    recognized_text: str
    overall_score: int
    word_accuracy: int
    transcript_similarity: int
    browser_confidence: float | None
    feedback: str
    focus_sound: str | None
    missing_words: list[str] = Field(default_factory=list)
    extra_words: list[str] = Field(default_factory=list)
    created_at: datetime


class PronunciationStats(BaseModel):
    total_attempts: int
    average_score: int | None
    best_score: int | None
    attempts_last_7_days: int
