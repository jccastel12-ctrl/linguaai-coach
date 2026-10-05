"""Initial schema: languages, users, student profiles, learning languages, lessons, progress.

Revision ID: 001
Revises:
Create Date: 2026-10-01
"""
from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "001"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

CEFR = "('A1', 'A2', 'B1', 'B2', 'C1', 'C2')"


def _timestamps() -> list[sa.Column]:
    return [
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    ]


def upgrade() -> None:
    languages = op.create_table(
        "languages",
        sa.Column("code", sa.String(8), nullable=False),
        sa.Column("name", sa.String(64), nullable=False),
        sa.Column("native_name", sa.String(64), nullable=False),
        sa.Column("is_active", sa.Boolean(), server_default=sa.true(), nullable=False),
        *_timestamps(),
        sa.PrimaryKeyConstraint("code", name="pk_languages"),
    )

    op.create_table(
        "users",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("email", sa.String(320), nullable=False),
        sa.Column("hashed_password", sa.String(255), nullable=False),
        sa.Column("full_name", sa.String(120), nullable=True),
        sa.Column("is_active", sa.Boolean(), server_default=sa.true(), nullable=False),
        sa.Column("is_superuser", sa.Boolean(), server_default=sa.false(), nullable=False),
        *_timestamps(),
        sa.PrimaryKeyConstraint("id", name="pk_users"),
    )
    op.create_index("ix_users_email", "users", ["email"], unique=True)

    op.create_table(
        "student_profiles",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("display_name", sa.String(80), nullable=True),
        sa.Column("native_language_code", sa.String(8), nullable=True),
        sa.Column("timezone", sa.String(64), server_default="UTC", nullable=False),
        sa.Column("daily_goal_minutes", sa.Integer(), server_default="15", nullable=False),
        sa.Column("bio", sa.Text(), nullable=True),
        *_timestamps(),
        sa.PrimaryKeyConstraint("id", name="pk_student_profiles"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], name="fk_student_profiles_user_id_users", ondelete="CASCADE"),
        sa.ForeignKeyConstraint(
            ["native_language_code"], ["languages.code"],
            name="fk_student_profiles_native_language_code_languages", ondelete="SET NULL",
        ),
        sa.UniqueConstraint("user_id", name="uq_student_profiles_user_id"),
        sa.CheckConstraint("daily_goal_minutes BETWEEN 1 AND 480", name="ck_student_profiles_daily_goal_range"),
    )

    op.create_table(
        "user_languages",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("language_code", sa.String(8), nullable=False),
        sa.Column("cefr_level", sa.String(2), server_default="A1", nullable=False),
        sa.Column("is_primary", sa.Boolean(), server_default=sa.false(), nullable=False),
        *_timestamps(),
        sa.PrimaryKeyConstraint("id", name="pk_user_languages"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], name="fk_user_languages_user_id_users", ondelete="CASCADE"),
        sa.ForeignKeyConstraint(
            ["language_code"], ["languages.code"], name="fk_user_languages_language_code_languages", ondelete="RESTRICT"
        ),
        sa.UniqueConstraint("user_id", "language_code", name="uq_user_languages_user_language"),
        sa.CheckConstraint(f"cefr_level IN {CEFR}", name="ck_user_languages_cefr_level_valid"),
    )
    op.create_index("ix_user_languages_user_id", "user_languages", ["user_id"])

    op.create_table(
        "lessons",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("language_code", sa.String(8), nullable=False),
        sa.Column("slug", sa.String(120), nullable=False),
        sa.Column("title", sa.String(200), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("cefr_level", sa.String(2), nullable=False),
        sa.Column("order_index", sa.Integer(), server_default="0", nullable=False),
        sa.Column("estimated_minutes", sa.Integer(), server_default="10", nullable=False),
        sa.Column("content", sa.JSON(), nullable=False),
        sa.Column("is_published", sa.Boolean(), server_default=sa.false(), nullable=False),
        *_timestamps(),
        sa.PrimaryKeyConstraint("id", name="pk_lessons"),
        sa.ForeignKeyConstraint(
            ["language_code"], ["languages.code"], name="fk_lessons_language_code_languages", ondelete="RESTRICT"
        ),
        sa.UniqueConstraint("language_code", "slug", name="uq_lessons_language_slug"),
        sa.CheckConstraint(f"cefr_level IN {CEFR}", name="ck_lessons_cefr_level_valid"),
        sa.CheckConstraint("estimated_minutes > 0", name="ck_lessons_estimated_minutes_positive"),
    )
    op.create_index("ix_lessons_language_code", "lessons", ["language_code"])

    op.create_table(
        "lesson_progress",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("lesson_id", sa.Uuid(), nullable=False),
        sa.Column("status", sa.String(20), server_default="not_started", nullable=False),
        sa.Column("score", sa.Integer(), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        *_timestamps(),
        sa.PrimaryKeyConstraint("id", name="pk_lesson_progress"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], name="fk_lesson_progress_user_id_users", ondelete="CASCADE"),
        sa.ForeignKeyConstraint(
            ["lesson_id"], ["lessons.id"], name="fk_lesson_progress_lesson_id_lessons", ondelete="CASCADE"
        ),
        sa.UniqueConstraint("user_id", "lesson_id", name="uq_lesson_progress_user_lesson"),
        sa.CheckConstraint(
            "status IN ('not_started', 'in_progress', 'completed')", name="ck_lesson_progress_status_valid"
        ),
        sa.CheckConstraint("score IS NULL OR (score BETWEEN 0 AND 100)", name="ck_lesson_progress_score_range"),
    )
    op.create_index("ix_lesson_progress_user_id", "lesson_progress", ["user_id"])
    op.create_index("ix_lesson_progress_lesson_id", "lesson_progress", ["lesson_id"])

    # Reference data: launch languages.
    op.bulk_insert(
        languages,
        [
            {"code": "es", "name": "Spanish", "native_name": "Español", "is_active": True},
            {"code": "en", "name": "English", "native_name": "English", "is_active": True},
            {"code": "sr", "name": "Serbian", "native_name": "Српски / Srpski", "is_active": True},
        ],
    )


def downgrade() -> None:
    op.drop_table("lesson_progress")
    op.drop_table("lessons")
    op.drop_table("user_languages")
    op.drop_table("student_profiles")
    op.drop_index("ix_users_email", table_name="users")
    op.drop_table("users")
    op.drop_table("languages")
