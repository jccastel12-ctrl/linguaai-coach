"""Tutor conversacional de texto y memoria pedagógica.

Revision ID: 002
Revises: 001
Create Date: 2026-10-04
"""
from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "002"
down_revision: str | None = "001"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

CEFR = "('A1', 'A2', 'B1', 'B2', 'C1', 'C2')"


def _timestamps() -> list[sa.Column]:
    return [
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    ]


def upgrade() -> None:
    op.create_table(
        "tutor_sessions",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("target_language_code", sa.String(length=8), nullable=False),
        sa.Column("cefr_level", sa.String(length=2), server_default="A1", nullable=False),
        sa.Column("personality", sa.String(length=20), server_default="patient", nullable=False),
        sa.Column("title", sa.String(length=120), nullable=True),
        *_timestamps(),
        sa.PrimaryKeyConstraint("id", name="pk_tutor_sessions"),
        sa.ForeignKeyConstraint(
            ["user_id"], ["users.id"], name="fk_tutor_sessions_user_id_users", ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(
            ["target_language_code"],
            ["languages.code"],
            name="fk_tutor_sessions_target_language_code_languages",
            ondelete="RESTRICT",
        ),
        sa.CheckConstraint(f"cefr_level IN {CEFR}", name="ck_tutor_sessions_cefr_level_valid"),
        sa.CheckConstraint(
            "personality IN ('friendly', 'patient', 'professional')",
            name="ck_tutor_sessions_personality_valid",
        ),
    )
    op.create_index("ix_tutor_sessions_user_id", "tutor_sessions", ["user_id"])

    op.create_table(
        "tutor_turns",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("session_id", sa.Uuid(), nullable=False),
        sa.Column("role", sa.String(length=12), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("corrected_text", sa.Text(), nullable=True),
        sa.Column("explanation", sa.Text(), nullable=True),
        sa.Column("translation", sa.Text(), nullable=True),
        sa.Column("feedback_meta", sa.JSON(), nullable=True),
        *_timestamps(),
        sa.PrimaryKeyConstraint("id", name="pk_tutor_turns"),
        sa.ForeignKeyConstraint(
            ["session_id"], ["tutor_sessions.id"], name="fk_tutor_turns_session_id_tutor_sessions", ondelete="CASCADE"
        ),
        sa.CheckConstraint("role IN ('user', 'assistant')", name="ck_tutor_turns_role_valid"),
    )
    op.create_index("ix_tutor_turns_session_id", "tutor_turns", ["session_id"])

    op.create_table(
        "learning_memories",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("language_code", sa.String(length=8), nullable=False),
        sa.Column("category", sa.String(length=24), nullable=False),
        sa.Column("memory_key", sa.String(length=120), nullable=False),
        sa.Column("note", sa.Text(), nullable=False),
        sa.Column("occurrence_count", sa.Integer(), server_default="1", nullable=False),
        sa.Column("last_example", sa.Text(), nullable=True),
        *_timestamps(),
        sa.PrimaryKeyConstraint("id", name="pk_learning_memories"),
        sa.ForeignKeyConstraint(
            ["user_id"], ["users.id"], name="fk_learning_memories_user_id_users", ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(
            ["language_code"],
            ["languages.code"],
            name="fk_learning_memories_language_code_languages",
            ondelete="RESTRICT",
        ),
        sa.UniqueConstraint(
            "user_id", "language_code", "category", "memory_key", name="uq_learning_memory_key"
        ),
        sa.CheckConstraint(
            "category IN ('grammar', 'vocabulary', 'pronunciation', 'usage')",
            name="ck_learning_memories_category_valid",
        ),
        sa.CheckConstraint("occurrence_count > 0", name="ck_learning_memories_occurrence_count_positive"),
    )
    op.create_index("ix_learning_memories_user_id", "learning_memories", ["user_id"])


def downgrade() -> None:
    op.drop_index("ix_learning_memories_user_id", table_name="learning_memories")
    op.drop_table("learning_memories")
    op.drop_index("ix_tutor_turns_session_id", table_name="tutor_turns")
    op.drop_table("tutor_turns")
    op.drop_index("ix_tutor_sessions_user_id", table_name="tutor_sessions")
    op.drop_table("tutor_sessions")
