import uuid

from sqlalchemy import CheckConstraint, Float, ForeignKey, Integer, String, Text, Uuid
from sqlalchemy.orm import Mapped, mapped_column

from app.core.constants import CEFR_LEVELS, sql_in
from app.core.database import Base, TimestampMixin


class PronunciationAttempt(Base, TimestampMixin):
    __tablename__ = "pronunciation_attempts"
    __table_args__ = (
        CheckConstraint(f"cefr_level IN {sql_in(CEFR_LEVELS)}", name="cefr_level_valid"),
        CheckConstraint("overall_score BETWEEN 0 AND 100", name="overall_score_range"),
        CheckConstraint("word_accuracy BETWEEN 0 AND 100", name="word_accuracy_range"),
        CheckConstraint("transcript_similarity BETWEEN 0 AND 100", name="transcript_similarity_range"),
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False
    )
    language_code: Mapped[str] = mapped_column(
        ForeignKey("languages.code", ondelete="RESTRICT"), nullable=False
    )
    cefr_level: Mapped[str] = mapped_column(String(2), nullable=False)
    expected_text: Mapped[str] = mapped_column(Text, nullable=False)
    recognized_text: Mapped[str] = mapped_column(Text, nullable=False)
    overall_score: Mapped[int] = mapped_column(Integer, nullable=False)
    word_accuracy: Mapped[int] = mapped_column(Integer, nullable=False)
    transcript_similarity: Mapped[int] = mapped_column(Integer, nullable=False)
    browser_confidence: Mapped[float | None] = mapped_column(Float)
    feedback: Mapped[str] = mapped_column(Text, nullable=False)
    focus_sound: Mapped[str | None] = mapped_column(String(80))
