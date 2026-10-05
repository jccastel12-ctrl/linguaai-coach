"""Pronunciation practice attempts.

Revision ID: 003
Revises: 002
Create Date: 2026-10-04
"""
from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "003"
down_revision: str | None = "002"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

CEFR = "('A1', 'A2', 'B1', 'B2', 'C1', 'C2')"


def upgrade() -> None:
    op.create_table(
        "pronunciation_attempts",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("language_code", sa.String(length=8), nullable=False),
        sa.Column("cefr_level", sa.String(length=2), nullable=False),
        sa.Column("expected_text", sa.Text(), nullable=False),
        sa.Column("recognized_text", sa.Text(), nullable=False),
        sa.Column("overall_score", sa.Integer(), nullable=False),
        sa.Column("word_accuracy", sa.Integer(), nullable=False),
        sa.Column("transcript_similarity", sa.Integer(), nullable=False),
        sa.Column("browser_confidence", sa.Float(), nullable=True),
        sa.Column("feedback", sa.Text(), nullable=False),
        sa.Column("focus_sound", sa.String(length=80), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id", name="pk_pronunciation_attempts"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], name="fk_pronunciation_attempts_user_id_users", ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["language_code"], ["languages.code"], name="fk_pronunciation_attempts_language_code_languages", ondelete="RESTRICT"),
        sa.CheckConstraint(f"cefr_level IN {CEFR}", name="ck_pronunciation_attempts_cefr_level_valid"),
        sa.CheckConstraint("overall_score BETWEEN 0 AND 100", name="ck_pronunciation_attempts_overall_score_range"),
        sa.CheckConstraint("word_accuracy BETWEEN 0 AND 100", name="ck_pronunciation_attempts_word_accuracy_range"),
        sa.CheckConstraint("transcript_similarity BETWEEN 0 AND 100", name="ck_pronunciation_attempts_transcript_similarity_range"),
    )
    op.create_index("ix_pronunciation_attempts_user_id", "pronunciation_attempts", ["user_id"])


def downgrade() -> None:
    op.drop_index("ix_pronunciation_attempts_user_id", table_name="pronunciation_attempts")
    op.drop_table("pronunciation_attempts")
