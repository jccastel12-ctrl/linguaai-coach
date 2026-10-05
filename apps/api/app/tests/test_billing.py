from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domains.billing.models import Subscription, UsageEvent
from app.domains.users.models import User

BASE = "/api/v1/billing"


async def test_plan_catalog_is_public(client: AsyncClient) -> None:
    response = await client.get(f"{BASE}/plans")
    assert response.status_code == 200
    body = response.json()
    assert [item["id"] for item in body] == ["basic", "pro"]
    assert body[0]["limits"]["tutor_messages_per_day"] == 20
    assert body[1]["limits"]["tutor_messages_per_day"] > body[0]["limits"]["tutor_messages_per_day"]
    assert body[1]["payment_enabled"] is False


async def test_new_user_gets_basic_overview(client: AsyncClient, auth_headers: dict[str, str]) -> None:
    response = await client.get(f"{BASE}/me", headers=auth_headers)
    assert response.status_code == 200
    body = response.json()
    assert body["plan"]["id"] == "basic"
    assert body["status"] == "active"
    assert all(item["used"] == 0 for item in body["usage"])


async def test_successful_translation_records_usage(client: AsyncClient, auth_headers: dict[str, str]) -> None:
    response = await client.post(
        "/api/v1/translate",
        headers=auth_headers,
        json={"text": "Necesito ayuda", "source_language": "es", "target_language": "en"},
    )
    assert response.status_code == 200

    overview = (await client.get(f"{BASE}/me", headers=auth_headers)).json()
    translation = next(item for item in overview["usage"] if item["feature"] == "translation")
    assert translation["used"] == 1
    assert translation["remaining"] == translation["limit"] - 1


async def test_basic_translation_limit_returns_429(
    client: AsyncClient,
    auth_headers: dict[str, str],
    db_session: AsyncSession,
) -> None:
    user = await db_session.scalar(select(User).where(User.email == "ana@example.com"))
    assert user is not None
    db_session.add_all([UsageEvent(user_id=user.id, feature="translation") for _ in range(30)])
    await db_session.commit()

    response = await client.post(
        "/api/v1/translate",
        headers=auth_headers,
        json={"text": "Necesito ayuda", "source_language": "es", "target_language": "en"},
    )
    assert response.status_code == 429
    assert "límite diario" in response.json()["detail"]


async def test_pro_has_higher_translation_limit(
    client: AsyncClient,
    auth_headers: dict[str, str],
    db_session: AsyncSession,
) -> None:
    user = await db_session.scalar(select(User).where(User.email == "ana@example.com"))
    assert user is not None
    subscription = await db_session.scalar(select(Subscription).where(Subscription.user_id == user.id))
    assert subscription is not None
    subscription.plan_tier = "pro"
    db_session.add_all([UsageEvent(user_id=user.id, feature="translation") for _ in range(30)])
    await db_session.commit()

    response = await client.post(
        "/api/v1/translate",
        headers=auth_headers,
        json={"text": "Necesito ayuda", "source_language": "es", "target_language": "en"},
    )
    assert response.status_code == 200


async def test_upgrade_request_does_not_activate_pro(client: AsyncClient, auth_headers: dict[str, str]) -> None:
    response = await client.post(f"{BASE}/me/request-upgrade", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["requested_plan"] == "pro"

    overview = (await client.get(f"{BASE}/me", headers=auth_headers)).json()
    assert overview["plan"]["id"] == "basic"
    assert overview["requested_plan"] == "pro"


async def test_payment_capabilities_are_explicitly_disabled(client: AsyncClient) -> None:
    response = await client.get(f"{BASE}/payment-capabilities")
    assert response.status_code == 200
    body = response.json()
    assert body["provider"] == "disabled"
    assert body["checkout_enabled"] is False
    assert body["webhooks_enabled"] is False
