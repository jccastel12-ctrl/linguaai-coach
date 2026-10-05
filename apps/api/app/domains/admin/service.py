import uuid
from datetime import datetime, timedelta, timezone

from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.domains.admin.schemas import AdminSubscriptionUpdate
from app.domains.billing.models import BillingAuditEvent, Subscription, UsageEvent
from app.domains.billing.service import get_or_create_subscription, utc_day_window
from app.domains.users.models import User


async def overview(db: AsyncSession) -> dict:
    seven_days_ago = datetime.now(timezone.utc) - timedelta(days=7)
    start, end = utc_day_window()

    total_users = int(await db.scalar(select(func.count(User.id))) or 0)
    active_users = int(await db.scalar(select(func.count(User.id)).where(User.is_active.is_(True))) or 0)
    new_users = int(await db.scalar(select(func.count(User.id)).where(User.created_at >= seven_days_ago)) or 0)
    pro_users = int(
        await db.scalar(
            select(func.count(Subscription.id)).where(
                Subscription.plan_tier == "pro", Subscription.status == "active"
            )
        )
        or 0
    )
    pending = int(
        await db.scalar(select(func.count(Subscription.id)).where(Subscription.requested_plan == "pro")) or 0
    )

    usage_rows = (
        await db.execute(
            select(UsageEvent.feature, func.coalesce(func.sum(UsageEvent.units), 0))
            .where(UsageEvent.created_at >= start, UsageEvent.created_at < end)
            .group_by(UsageEvent.feature)
        )
    ).all()
    usage = {"tutor_message": 0, "translation": 0, "pronunciation": 0}
    for feature, units in usage_rows:
        if feature in usage:
            usage[feature] = int(units or 0)

    return {
        "total_users": total_users,
        "active_users": active_users,
        "pro_users": pro_users,
        "pending_upgrade_requests": pending,
        "new_users_last_7_days": new_users,
        "usage_today": usage,
        "payment_provider": settings.payment_provider,
        # v1.0 deliberately ships without real checkout/webhooks.
        "checkout_enabled": False,
    }


async def list_users(
    db: AsyncSession,
    *,
    search: str | None = None,
    limit: int = 50,
    offset: int = 0,
    upgrade_requests_only: bool = False,
) -> dict:
    conditions = []
    if search:
        needle = f"%{search.strip()}%"
        conditions.append(or_(User.email.ilike(needle), User.full_name.ilike(needle)))
    if upgrade_requests_only:
        conditions.append(Subscription.requested_plan == "pro")

    base = select(User, Subscription).outerjoin(Subscription, Subscription.user_id == User.id)
    count_query = select(func.count(User.id)).outerjoin(Subscription, Subscription.user_id == User.id)
    for condition in conditions:
        base = base.where(condition)
        count_query = count_query.where(condition)

    total = int(await db.scalar(count_query) or 0)
    rows = (await db.execute(base.order_by(User.created_at.desc()).limit(limit).offset(offset))).all()
    items = []
    for user, subscription in rows:
        items.append(
            {
                "id": user.id,
                "email": user.email,
                "full_name": user.full_name,
                "is_active": user.is_active,
                "is_superuser": user.is_superuser,
                "created_at": user.created_at,
                "plan_tier": subscription.plan_tier if subscription else "basic",
                "subscription_status": subscription.status if subscription else "active",
                "requested_plan": subscription.requested_plan if subscription else None,
                "payment_provider": subscription.payment_provider if subscription else None,
            }
        )
    return {"items": items, "total": total, "limit": limit, "offset": offset}


async def set_subscription(
    db: AsyncSession,
    *,
    actor: User,
    target_user_id: uuid.UUID,
    data: AdminSubscriptionUpdate,
) -> dict | None:
    target = await db.get(User, target_user_id)
    if target is None:
        return None
    subscription = await get_or_create_subscription(db, target)
    old_plan = subscription.plan_tier
    subscription.plan_tier = data.plan_tier
    subscription.status = data.status
    if subscription.payment_provider is None:
        subscription.payment_provider = "manual"
    if subscription.requested_plan == data.plan_tier:
        subscription.requested_plan = None

    db.add(
        BillingAuditEvent(
            actor_user_id=actor.id,
            target_user_id=target.id,
            action="subscription_changed",
            old_plan=old_plan,
            new_plan=data.plan_tier,
            note=data.note or "Cambio manual desde el panel administrativo.",
        )
    )
    await db.commit()
    return (await list_users(db, search=target.email, limit=1, offset=0))["items"][0]


async def set_user_active(
    db: AsyncSession,
    *,
    actor: User,
    target_user_id: uuid.UUID,
    is_active: bool,
    note: str | None = None,
) -> User | None:
    target = await db.get(User, target_user_id)
    if target is None:
        return None
    if target.id == actor.id and not is_active:
        raise ValueError("No puedes desactivar tu propia cuenta administrativa.")
    target.is_active = is_active
    db.add(
        BillingAuditEvent(
            actor_user_id=actor.id,
            target_user_id=target.id,
            action="user_activated" if is_active else "user_deactivated",
            note=note or "Cambio manual desde el panel administrativo.",
        )
    )
    await db.commit()
    await db.refresh(target)
    return target


async def list_audit(db: AsyncSession, *, limit: int = 25) -> list[BillingAuditEvent]:
    result = await db.scalars(select(BillingAuditEvent).order_by(BillingAuditEvent.created_at.desc()).limit(limit))
    return list(result.all())
