from app.domains.auth import service as auth_service
from app.domains.users.service import get_user_by_email


async def test_password_reset_request_does_not_enumerate_accounts(client):
    existing = await client.post(
        "/api/v1/auth/password-reset/request", json={"email": "missing@example.com"}
    )
    assert existing.status_code == 202


async def test_password_reset_token_changes_password_and_invalidates_old_token(client, db_session):
    payload = {"email": "reset@example.com", "password": "old-password-123", "full_name": "Reset"}
    assert (await client.post("/api/v1/auth/register", json=payload)).status_code == 201
    login = await client.post("/api/v1/auth/login", json={"email": payload["email"], "password": payload["password"]})
    old_access = login.json()["access_token"]

    user = await get_user_by_email(db_session, payload["email"])
    raw = await auth_service.create_account_token(db_session, user, purpose="password_reset", lifetime_minutes=60)
    reset = await client.post("/api/v1/auth/password-reset/confirm", json={"token": raw, "new_password": "new-password-456"})
    assert reset.status_code == 200

    old_me = await client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {old_access}"})
    assert old_me.status_code == 401
    new_login = await client.post("/api/v1/auth/login", json={"email": payload["email"], "password": "new-password-456"})
    assert new_login.status_code == 200


async def test_email_verification_token(client, db_session):
    payload = {"email": "verify@example.com", "password": "supersecret123!", "full_name": "Verify"}
    assert (await client.post("/api/v1/auth/register", json=payload)).status_code == 201
    user = await get_user_by_email(db_session, payload["email"])
    raw = await auth_service.create_account_token(db_session, user, purpose="email_verification", lifetime_minutes=60)
    response = await client.post("/api/v1/auth/email-verification/confirm", json={"token": raw})
    assert response.status_code == 200
    assert response.json()["email_verified_at"] is not None


async def test_change_password_requires_current_password(client, auth_headers):
    bad = await client.post(
        "/api/v1/auth/password/change",
        headers=auth_headers,
        json={"current_password": "wrong", "new_password": "new-password-789"},
    )
    assert bad.status_code == 400
