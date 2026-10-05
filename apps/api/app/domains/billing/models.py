import uuid
from datetime import datetime

from sqlalchemy import Boolean, CheckConstraint, DateTime, ForeignKey, Index, Integer, String, Text, Uuid, false
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base, TimestampMixin


class Subscription(Base, TimestampMixin):
    """Current commercial tier for one user.

    v1.0 keeps payment processing disabled by default, but stores provider-facing
    identifiers so a future checkout/webhook integration can synchronize the
    same subscription row instead of introducing a parallel billing model.
    """

    __tablename__ = "subscriptions"
    __table_args__ = (
        CheckConstraint("plan_tier IN ('basic', 'pro')", name="plan_tier_valid"),
        CheckConstraint("status IN ('active', 'canceled', 'past_due')", name="status_valid"),
        CheckConstraint("requested_plan IS NULL OR requested_plan IN ('basic', 'pro')", name="requested_plan_valid"),
        CheckConstraint(
            "payment_provider IS NULL OR payment_provider IN ('manual', 'stripe')",
            name="payment_provider_valid",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), unique=True, index=True, nullable=False
    )
    plan_tier: Mapped[str] = mapped_column(String(16), default="basic", server_default="basic", nullable=False)
    status: Mapped[str] = mapped_column(String(16), default="active", server_default="active", nullable=False)
    requested_plan: Mapped[str | None] = mapped_column(String(16))

    # Provider-neutral fields. They remain NULL while checkout is disabled.
    payment_provider: Mapped[str | None] = mapped_column(String(32))
    external_customer_id: Mapped[str | None] = mapped_column(String(160))
    external_subscription_id: Mapped[str | None] = mapped_column(String(160))
    current_period_end: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    cancel_at_period_end: Mapped[bool] = mapped_column(Boolean, default=False, server_default=false(), nullable=False)


class UsageEvent(Base, TimestampMixin):
    """Successful metered action used to enforce daily plan quotas."""

    __tablename__ = "usage_events"
    __table_args__ = (
        CheckConstraint(
            "feature IN ('tutor_message', 'translation', 'pronunciation')",
            name="feature_valid",
        ),
        CheckConstraint("units >= 1", name="units_positive"),
        Index("ix_usage_events_user_feature_created", "user_id", "feature", "created_at"),
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    feature: Mapped[str] = mapped_column(String(32), nullable=False)
    units: Mapped[int] = mapped_column(Integer, default=1, server_default="1", nullable=False)


class BillingAuditEvent(Base, TimestampMixin):
    """Immutable-ish audit trail for manual/admin billing changes.

    This is intentionally separate from payment-provider webhooks. It records
    who changed a local entitlement and why, which is useful before and after a
    real payment provider is connected.
    """

    __tablename__ = "billing_audit_events"
    __table_args__ = (Index("ix_billing_audit_target_created", "target_user_id", "created_at"),)

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    actor_user_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True
    )
    target_user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    action: Mapped[str] = mapped_column(String(64), nullable=False)
    old_plan: Mapped[str | None] = mapped_column(String(16))
    new_plan: Mapped[str | None] = mapped_column(String(16))
    note: Mapped[str | None] = mapped_column(Text)
