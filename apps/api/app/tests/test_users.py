from httpx import AsyncClient

REGISTER = "/api/v1/auth/register"
LOGIN = "/api/v1/auth/login"
ME = "/api/v1/users/me"
AUTH_ME = "/api/v1/auth/me"


# ---------------------------------------------------------------------------
# Registration
# ---------------------------------------------------------------------------


async def test_register_creates_user_with_profile(client: AsyncClient) -> None:
    res = await client.post(
        REGISTER, json={"email": "Marko@Example.com", "password": "supersecret123!", "full_name": "Marko"}
    )
    assert res.status_code == 201
    body = res.json()
    assert body["email"] == "marko@example.com"  # normalized
    assert body["profile"]["daily_goal_minutes"] == 15
    assert "hashed_password" not in body and "password" not in body


async def test_register_rejects_duplicate_email(client: AsyncClient) -> None:
    payload = {"email": "dup@example.com", "password": "supersecret123!"}
    assert (await client.post(REGISTER, json=payload)).status_code == 201
    assert (await client.post(REGISTER, json={**payload, "email": "DUP@example.com"})).status_code == 409


async def test_register_rejects_weak_password(client: AsyncClient) -> None:
    res = await client.post(REGISTER, json={"email": "weak@example.com", "password": "short"})
    assert res.status_code == 422


# ---------------------------------------------------------------------------
# Login
# ---------------------------------------------------------------------------


async def test_login_wrong_password_returns_401(client: AsyncClient, auth_headers: dict[str, str]) -> None:
    res = await client.post(LOGIN, json={"email": "ana@example.com", "password": "wrongpassword!"})
    assert res.status_code == 401


async def test_login_returns_token(client: AsyncClient, auth_headers: dict[str, str]) -> None:
    res = await client.post(LOGIN, json={"email": "ana@example.com", "password": "supersecret123!"})
    assert res.status_code == 200
    body = res.json()
    assert "access_token" in body
    assert body["token_type"] == "bearer"
    assert body["expires_in"] > 0


# ---------------------------------------------------------------------------
# /users/me (existing endpoint)
# ---------------------------------------------------------------------------


async def test_me_requires_authentication(client: AsyncClient) -> None:
    assert (await client.get(ME)).status_code == 401
    assert (await client.get(ME, headers={"Authorization": "Bearer not-a-jwt"})).status_code == 401


async def test_me_returns_current_user(client: AsyncClient, auth_headers: dict[str, str]) -> None:
    res = await client.get(ME, headers=auth_headers)
    assert res.status_code == 200
    assert res.json()["email"] == "ana@example.com"


# ---------------------------------------------------------------------------
# /auth/me (new endpoint — mirrors /users/me)
# ---------------------------------------------------------------------------


async def test_auth_me_requires_authentication(client: AsyncClient) -> None:
    assert (await client.get(AUTH_ME)).status_code == 401
    assert (await client.get(AUTH_ME, headers={"Authorization": "Bearer invalid.token.here"})).status_code == 401


async def test_auth_me_returns_current_user(client: AsyncClient, auth_headers: dict[str, str]) -> None:
    res = await client.get(AUTH_ME, headers=auth_headers)
    assert res.status_code == 200
    body = res.json()
    assert body["email"] == "ana@example.com"
    assert "hashed_password" not in body


async def test_auth_me_matches_users_me(client: AsyncClient, auth_headers: dict[str, str]) -> None:
    """Both /auth/me and /users/me must return identical payloads."""
    r1 = await client.get(AUTH_ME, headers=auth_headers)
    r2 = await client.get(ME, headers=auth_headers)
    assert r1.status_code == r2.status_code == 200
    assert r1.json() == r2.json()


# ---------------------------------------------------------------------------
# Profile & language update
# ---------------------------------------------------------------------------


async def test_update_profile_and_learning_language(client: AsyncClient, auth_headers: dict[str, str]) -> None:
    res = await client.patch(
        f"{ME}/profile", headers=auth_headers, json={"native_language_code": "es", "daily_goal_minutes": 30}
    )
    assert res.status_code == 200
    assert res.json()["native_language_code"] == "es"

    res = await client.put(
        f"{ME}/languages", headers=auth_headers, json={"language_code": "sr", "cefr_level": "A2", "is_primary": True}
    )
    assert res.status_code == 200
    assert res.json() == {"language_code": "sr", "cefr_level": "A2", "is_primary": True}

    me = (await client.get(ME, headers=auth_headers)).json()
    assert me["languages"][0]["language_code"] == "sr"


async def test_update_profile_rejects_unknown_language(client: AsyncClient, auth_headers: dict[str, str]) -> None:
    res = await client.patch(f"{ME}/profile", headers=auth_headers, json={"native_language_code": "xx"})
    assert res.status_code == 422
