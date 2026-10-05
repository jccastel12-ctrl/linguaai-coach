"""Admin billing audit and payment-provider readiness.

Revision ID: 005
Revises: 004
Create Date: 2026-10-04
"""
from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "005"
down_revision: str | None = "004"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # batch_alter_table keeps this migration executable in the SQLite migration test
    # while emitting ordinary ALTER statements on PostgreSQL.
    with op.batch_alter_table("subscriptions") as batch_op:
        batch_op.add_column(sa.Column("payment_provider", sa.String(length=32), nullable=True))
        batch_op.add_column(sa.Column("external_customer_id", sa.String(length=160), nullable=True))
        batch_op.add_column(sa.Column("external_subscription_id", sa.String(length=160), nullable=True))
        batch_op.add_column(sa.Column("current_period_end", sa.DateTime(timezone=True), nullable=True))
        batch_op.add_column(
            sa.Column("cancel_at_period_end", sa.Boolean(), server_default=sa.false(), nullable=False)
        )
        batch_op.create_check_constraint(
            "ck_subscriptions_payment_provider_valid",
            "payment_provider IS NULL OR payment_provider IN ('manual', 'stripe')",
        )

    op.create_table(
        "billing_audit_events",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("actor_user_id", sa.Uuid(), nullable=True),
        sa.Column("target_user_id", sa.Uuid(), nullable=False),
        sa.Column("action", sa.String(length=64), nullable=False),
        sa.Column("old_plan", sa.String(length=16), nullable=True),
        sa.Column("new_plan", sa.String(length=16), nullable=True),
        sa.Column("note", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id", name="pk_billing_audit_events"),
        sa.ForeignKeyConstraint(
            ["actor_user_id"], ["users.id"], name="fk_billing_audit_events_actor_user_id_users", ondelete="SET NULL"
        ),
        sa.ForeignKeyConstraint(
            ["target_user_id"], ["users.id"], name="fk_billing_audit_events_target_user_id_users", ondelete="CASCADE"
        ),
    )
    op.create_index("ix_billing_audit_events_actor_user_id", "billing_audit_events", ["actor_user_id"])
    op.create_index("ix_billing_audit_events_target_user_id", "billing_audit_events", ["target_user_id"])
    op.create_index(
        "ix_billing_audit_target_created", "billing_audit_events", ["target_user_id", "created_at"]
    )


def downgrade() -> None:
    op.drop_index("ix_billing_audit_target_created", table_name="billing_audit_events")
    op.drop_index("ix_billing_audit_events_target_user_id", table_name="billing_audit_events")
    op.drop_index("ix_billing_audit_events_actor_user_id", table_name="billing_audit_events")
    op.drop_table("billing_audit_events")

    with op.batch_alter_table("subscriptions") as batch_op:
        batch_op.drop_constraint("ck_subscriptions_payment_provider_valid", type_="check")
        batch_op.drop_column("cancel_at_period_end")
        batch_op.drop_column("current_period_end")
        batch_op.drop_column("external_subscription_id")
        batch_op.drop_column("external_customer_id")
        batch_op.drop_column("payment_provider")
