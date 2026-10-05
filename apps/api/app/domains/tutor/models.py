import uuid

from sqlalchemy import CheckConstraint, ForeignKey, Integer, JSON, String, Text, UniqueConstraint, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.constants import CEFR_LEVELS, sql_in
from app.core.database import Base, TimestampMixin

TUTOR_PERSONALITIES = ("friendly", "patient", "professional")
TURN_ROLES = ("user", "assistant")
MEMORY_CATEGORIES = ("grammar", "vocabulary", "pronunciation", "usage")


class TutorSession(Base, TimestampMixin):
    __tablename__ = "tutor_sessions"
    __table_args__ = (
        CheckConstraint(f"cefr_level IN {sql_in(CEFR_LEVELS)}", name="cefr_level_valid"),
        CheckConstraint(
            "personality IN ('friendly', 'patient', 'professional')", name="personality_valid"
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False
    )
    target_language_code: Mapped[str] = mapped_column(
        ForeignKey("languages.code", ondelete="RESTRICT"), nullable=False
    )
    cefr_level: Mapped[str] = mapped_column(String(2), nullable=False, default="A1", server_default="A1")
    personality: Mapped[str] = mapped_column(
        String(20), nullable=False, default="patient", server_default="patient"
    )
    title: Mapped[str | None] = mapped_column(String(120))

    turns: Mapped[list["TutorTurn"]] = relationship(
        back_populates="session",
        cascade="all, delete-orphan",
        lazy="selectin",
        order_by="TutorTurn.created_at",
    )


class TutorTurn(Base, TimestampMixin):
    __tablename__ = "tutor_turns"
    __table_args__ = (CheckConstraint("role IN ('user', 'assistant')", name="role_valid"),)

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    session_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("tutor_sessions.id", ondelete="CASCADE"), index=True, nullable=False
    )
    role: Mapped[str] = mapped_column(String(12), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    corrected_text: Mapped[str | None] = mapped_column(Text)
    explanation: Mapped[str | None] = mapped_column(Text)
    translation: Mapped[str | None] = mapped_column(Text)
    feedback_meta: Mapped[dict | None] = mapped_column(JSON)

    session: Mapped[TutorSession] = relationship(back_populates="turns")


class LearningMemory(Base, TimestampMixin):
    __tablename__ = "learning_memories"
    __table_args__ = (
        UniqueConstraint(
            "user_id", "language_code", "category", "memory_key", name="uq_learning_memory_key"
        ),
        CheckConstraint(
            "category IN ('grammar', 'vocabulary', 'pronunciation', 'usage')",
            name="category_valid",
        ),
        CheckConstraint("occurrence_count > 0", name="occurrence_count_positive"),
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False
    )
    language_code: Mapped[str] = mapped_column(
        ForeignKey("languages.code", ondelete="RESTRICT"), nullable=False
    )
    category: Mapped[str] = mapped_column(String(24), nullable=False)
    memory_key: Mapped[str] = mapped_column(String(120), nullable=False)
    note: Mapped[str] = mapped_column(Text, nullable=False)
    occurrence_count: Mapped[int] = mapped_column(Integer, nullable=False, default=1, server_default="1")
    last_example: Mapped[str | None] = mapped_column(Text)
