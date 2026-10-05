import uuid
from datetime import datetime

from sqlalchemy import (
    Boolean,
    DateTime,
    CheckConstraint,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
    Uuid,
    false,
    true,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.constants import CEFR_LEVELS, sql_in
from app.core.database import Base, TimestampMixin


class User(Base, TimestampMixin):
    """Authentication identity. Learning data lives in StudentProfile / UserLanguage."""

    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    email: Mapped[str] = mapped_column(String(320), unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[str | None] = mapped_column(String(120))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, server_default=true(), nullable=False)
    is_superuser: Mapped[bool] = mapped_column(Boolean, default=False, server_default=false(), nullable=False)
    email_verified_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    auth_version: Mapped[int] = mapped_column(Integer, default=0, server_default="0", nullable=False)

    profile: Mapped["StudentProfile | None"] = relationship(
        back_populates="user", uselist=False, cascade="all, delete-orphan", lazy="selectin"
    )
    languages: Mapped[list["UserLanguage"]] = relationship(
        back_populates="user", cascade="all, delete-orphan", lazy="selectin"
    )


class StudentProfile(Base, TimestampMixin):
    __tablename__ = "student_profiles"
    __table_args__ = (CheckConstraint("daily_goal_minutes BETWEEN 1 AND 480", name="daily_goal_range"),)

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    display_name: Mapped[str | None] = mapped_column(String(80))
    native_language_code: Mapped[str | None] = mapped_column(ForeignKey("languages.code", ondelete="SET NULL"))
    timezone: Mapped[str] = mapped_column(String(64), default="UTC", server_default="UTC", nullable=False)
    daily_goal_minutes: Mapped[int] = mapped_column(Integer, default=15, server_default="15", nullable=False)
    bio: Mapped[str | None] = mapped_column(Text)

    user: Mapped[User] = relationship(back_populates="profile")


class UserLanguage(Base, TimestampMixin):
    """A language the student is learning, with their current CEFR level."""

    __tablename__ = "user_languages"
    __table_args__ = (
        UniqueConstraint("user_id", "language_code", name="uq_user_languages_user_language"),
        CheckConstraint(f"cefr_level IN {sql_in(CEFR_LEVELS)}", name="cefr_level_valid"),
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    language_code: Mapped[str] = mapped_column(ForeignKey("languages.code", ondelete="RESTRICT"), nullable=False)
    cefr_level: Mapped[str] = mapped_column(String(2), default="A1", server_default="A1", nullable=False)
    is_primary: Mapped[bool] = mapped_column(Boolean, default=False, server_default=false(), nullable=False)

    user: Mapped[User] = relationship(back_populates="languages")
