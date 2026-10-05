from datetime import datetime, timedelta, timezone

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.domains.billing.models import Subscription, UsageEvent
from app.domains.billing.schemas import FeatureKey
from app.domains.users.models import User

FEATURE_META: dict[FeatureKey, tuple[str, str]] = {
    "tutor_message": ("Mensajes al Tutor IA", "tutor_messages_per_day"),
    "translation": ("Traducciones", "translations_per_day"),
    "pronunciation": ("Intentos de pronunciación", "pronunciation_attempts_per_day"),
}

PLAN_CATALOG: dict[str, dict] = {
    "basic": {
        "id": "basic",
        "name": "Basic",
        "tagline": "La base para aprender y practicar cada día.",
        "audience": "Estudiantes que quieren avanzar con una rutina constante.",
        "limits": {
            "tutor_messages_per_day": 20,
            "translations_per_day": 30,
            "pronunciation_attempts_per_day": 10,
        },
        "benefits": [
            "Tutor IA de texto y voz",
            "Traductor español, inglés y serbio",
            "Práctica de pronunciación",
            "Historial y seguimiento de progreso",
            "Avatar tutor ligero",
        ],
        "payment_enabled": False,
    },
    "pro": {
        "id": "pro",
        "name": "Pro",
        "tagline": "Más práctica diaria para aprendizaje intensivo.",
        "audience": "Usuarios frecuentes, viajeros y profesionales que necesitan mayor capacidad.",
        "limits": {
            "tutor_messages_per_day": 200,
            "translations_per_day": 500,
            "pronunciation_attempts_per_day": 100,
        },
        "benefits": [
            "Todo lo incluido en Basic",
            "Límites diarios ampliados",
            "Preparado para funciones de voz y análisis avanzados",
            "Prioridad para futuras funciones premium",
            "Arquitectura lista para checkout y facturación",
        ],
        "payment_enabled": False,
    },
}


class PlanLimitExceededError(RuntimeError):
    def __init__(self, feature: FeatureKey, used: int, limit: int):
        self.feature = feature
        self.used = used
        self.limit = limit
        label = FEATURE_META[feature][0]
        super().__init__(
            f"Alcanzaste el límite diario de {label.lower()} de tu plan. "
            "Puedes volver a intentarlo después del reinicio diario o consultar el plan Pro."
        )


def utc_day_window(now: datetime | None = None) -> tuple[datetime, datetime]:
    now = now or datetime.now(timezone.utc)
    start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    return start, start + timedelta(days=1)


def list_plans() -> list[dict]:
    return [PLAN_CATALOG["basic"], PLAN_CATALOG["pro"]]


async def get_or_create_subscription(db: AsyncSession, user: User) -> Subscription:
    subscription = await db.scalar(select(Subscription).where(Subscription.user_id == user.id))
    if subscription is None:
        subscription = Subscription(user_id=user.id, plan_tier="basic", status="active")
        db.add(subscription)
        await db.commit()
        await db.refresh(subscription)
    return subscription


async def _usage_count(db: AsyncSession, user: User, feature: FeatureKey) -> int:
    start, end = utc_day_window()
    total = await db.scalar(
        select(func.coalesce(func.sum(UsageEvent.units), 0)).where(
            UsageEvent.user_id == user.id,
            UsageEvent.feature == feature,
            UsageEvent.created_at >= start,
            UsageEvent.created_at < end,
        )
    )
    return int(total or 0)


async def check_feature_limit(db: AsyncSession, user: User, feature: FeatureKey) -> None:
    subscription = await get_or_create_subscription(db, user)
    plan = PLAN_CATALOG.get(subscription.plan_tier, PLAN_CATALOG["basic"])
    limit_key = FEATURE_META[feature][1]
    limit = int(plan["limits"][limit_key])
    used = await _usage_count(db, user, feature)
    if used >= limit:
        raise PlanLimitExceededError(feature, used, limit)


async def record_usage(db: AsyncSession, user: User, feature: FeatureKey, units: int = 1) -> None:
    db.add(UsageEvent(user_id=user.id, feature=feature, units=max(1, units)))
    await db.commit()


async def get_overview(db: AsyncSession, user: User) -> dict:
    subscription = await get_or_create_subscription(db, user)
    plan = PLAN_CATALOG.get(subscription.plan_tier, PLAN_CATALOG["basic"])
    usage: list[dict] = []
    for feature, (label, limit_key) in FEATURE_META.items():
        used = await _usage_count(db, user, feature)
        limit = int(plan["limits"][limit_key])
        usage.append(
            {
                "feature": feature,
                "label": label,
                "used": used,
                "limit": limit,
                "remaining": max(0, limit - used),
            }
        )
    _, resets_at = utc_day_window()
    return {
        "plan": plan,
        "status": subscription.status,
        "requested_plan": subscription.requested_plan,
        "usage": usage,
        "resets_at": resets_at,
        "payment_enabled": False,
    }


async def request_upgrade(db: AsyncSession, user: User) -> dict[str, str]:
    subscription = await get_or_create_subscription(db, user)
    if subscription.plan_tier == "pro":
        return {"requested_plan": "pro", "message": "Tu cuenta ya está en el plan Pro."}
    subscription.requested_plan = "pro"
    await db.commit()
    return {
        "requested_plan": "pro",
        "message": "Solicitud Pro registrada. El checkout todavía no está habilitado en esta versión.",
    }


def payment_capabilities() -> dict[str, object]:
    return {
        "provider": settings.payment_provider,
        "checkout_enabled": False,
        "webhooks_enabled": False,
        "note": (
            "El modelo de datos y las variables de entorno están preparados para un proveedor de pagos, "
            "pero v1.0 no inicia cobros ni procesa webhooks reales."
        ),
    }
