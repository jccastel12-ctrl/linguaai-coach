"""Basic/Pro subscriptions and metered usage.

Revision ID: 004
Revises: 003
Create Date: 2026-10-04
"""
from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "004"
down_revision: str | None = "003"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "subscriptions",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("plan_tier", sa.String(length=16), server_default="basic", nullable=False),
        sa.Column("status", sa.String(length=16), server_default="active", nullable=False),
        sa.Column("requested_plan", sa.String(length=16), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id", name="pk_subscriptions"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], name="fk_subscriptions_user_id_users", ondelete="CASCADE"),
        sa.UniqueConstraint("user_id", name="uq_subscriptions_user_id"),
        sa.CheckConstraint("plan_tier IN ('basic', 'pro')", name="ck_subscriptions_plan_tier_valid"),
        sa.CheckConstraint("status IN ('active', 'canceled', 'past_due')", name="ck_subscriptions_status_valid"),
        sa.CheckConstraint(
            "requested_plan IS NULL OR requested_plan IN ('basic', 'pro')",
            name="ck_subscriptions_requested_plan_valid",
        ),
    )
    op.create_index("ix_subscriptions_user_id", "subscriptions", ["user_id"])

    op.create_table(
        "usage_events",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("feature", sa.String(length=32), nullable=False),
        sa.Column("units", sa.Integer(), server_default="1", nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id", name="pk_usage_events"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], name="fk_usage_events_user_id_users", ondelete="CASCADE"),
        sa.CheckConstraint(
            "feature IN ('tutor_message', 'translation', 'pronunciation')",
            name="ck_usage_events_feature_valid",
        ),
        sa.CheckConstraint("units >= 1", name="ck_usage_events_units_positive"),
    )
    op.create_index(
        "ix_usage_events_user_feature_created",
        "usage_events",
        ["user_id", "feature", "created_at"],
    )


def downgrade() -> None:
    op.drop_index("ix_usage_events_user_feature_created", table_name="usage_events")
    op.drop_table("usage_events")
    op.drop_index("ix_subscriptions_user_id", table_name="subscriptions")
    op.drop_table("subscriptions")
