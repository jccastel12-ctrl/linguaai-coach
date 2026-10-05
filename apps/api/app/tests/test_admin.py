from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domains.billing.models import BillingAuditEvent
from app.domains.users.models import User

BASE = "/api/v1/admin"


async def test_non_admin_is_forbidden(client: AsyncClient, auth_headers: dict[str, str]) -> None:
    response = await client.get(f"{BASE}/overview", headers=auth_headers)
    assert response.status_code == 403


async def test_admin_overview(client: AsyncClient, admin_headers: dict[str, str]) -> None:
    response = await client.get(f"{BASE}/overview", headers=admin_headers)
    assert response.status_code == 200
    body = response.json()
    assert body["total_users"] >= 1
    assert body["active_users"] >= 1
    assert body["payment_provider"] == "disabled"
    assert body["checkout_enabled"] is False


async def test_admin_can_approve_pro_request(
    client: AsyncClient,
    auth_headers: dict[str, str],
    admin_headers: dict[str, str],
    db_session: AsyncSession,
) -> None:
    assert (await client.post("/api/v1/billing/me/request-upgrade", headers=auth_headers)).status_code == 200
    target = await db_session.scalar(select(User).where(User.email == "ana@example.com"))
    assert target is not None

    response = await client.patch(
        f"{BASE}/users/{target.id}/subscription",
        headers=admin_headers,
        json={"plan_tier": "pro", "status": "active", "note": "Aprobación manual de prueba"},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["plan_tier"] == "pro"
    assert body["requested_plan"] is None
    assert body["payment_provider"] == "manual"

    billing = (await client.get("/api/v1/billing/me", headers=auth_headers)).json()
    assert billing["plan"]["id"] == "pro"

    audit = await db_session.scalar(
        select(BillingAuditEvent).where(BillingAuditEvent.target_user_id == target.id)
    )
    assert audit is not None
    assert audit.action == "subscription_changed"
    assert audit.old_plan == "basic"
    assert audit.new_plan == "pro"


async def test_admin_user_listing_and_upgrade_filter(
    client: AsyncClient,
    auth_headers: dict[str, str],
    admin_headers: dict[str, str],
) -> None:
    assert (await client.post("/api/v1/billing/me/request-upgrade", headers=auth_headers)).status_code == 200

    listing = await client.get(f"{BASE}/users?search=ana%40example.com", headers=admin_headers)
    assert listing.status_code == 200
    assert listing.json()["total"] == 1

    pending = await client.get(f"{BASE}/users?upgrade_requests_only=true", headers=admin_headers)
    assert pending.status_code == 200
    assert any(item["email"] == "ana@example.com" for item in pending.json()["items"])


async def test_admin_cannot_deactivate_self(client: AsyncClient, admin_headers: dict[str, str], db_session: AsyncSession) -> None:
    admin = await db_session.scalar(select(User).where(User.email == "admin@example.com"))
    assert admin is not None
    response = await client.patch(
        f"{BASE}/users/{admin.id}/active",
        headers=admin_headers,
        json={"is_active": False},
    )
    assert response.status_code == 422
