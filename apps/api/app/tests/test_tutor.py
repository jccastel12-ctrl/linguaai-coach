from httpx import AsyncClient

BASE = "/api/v1/tutor"


async def test_tutor_requires_authentication(client: AsyncClient) -> None:
    assert (await client.get(f"{BASE}/sessions")).status_code == 401
    assert (
        await client.post(
            f"{BASE}/sessions",
            json={"target_language_code": "en", "cefr_level": "A1", "personality": "patient"},
        )
    ).status_code == 401


async def test_create_session_and_rule_based_correction(
    client: AsyncClient, auth_headers: dict[str, str]
) -> None:
    await client.patch(
        "/api/v1/users/me/profile",
        headers=auth_headers,
        json={"native_language_code": "es"},
    )
    created = await client.post(
        f"{BASE}/sessions",
        headers=auth_headers,
        json={"target_language_code": "en", "cefr_level": "A2", "personality": "patient"},
    )
    assert created.status_code == 201
    session_id = created.json()["id"]

    exchange = await client.post(
        f"{BASE}/sessions/{session_id}/messages",
        headers=auth_headers,
        json={"text": "I have 20 years old"},
    )
    assert exchange.status_code == 200
    body = exchange.json()
    assert body["assistant_turn"]["corrected_text"] == "I am 20 years old."
    assert "to be" in body["assistant_turn"]["explanation"]
    assert body["user_turn"]["content"] == "I have 20 years old"

    detail = await client.get(f"{BASE}/sessions/{session_id}", headers=auth_headers)
    assert detail.status_code == 200
    assert len(detail.json()["turns"]) == 2

    memory = await client.get(f"{BASE}/memory", headers=auth_headers)
    assert memory.status_code == 200
    assert memory.json()[0]["memory_key"] == "age_with_be"
    assert memory.json()[0]["occurrence_count"] == 1


async def test_memory_counts_repeated_error(client: AsyncClient, auth_headers: dict[str, str]) -> None:
    created = await client.post(
        f"{BASE}/sessions",
        headers=auth_headers,
        json={"target_language_code": "en", "cefr_level": "A1", "personality": "friendly"},
    )
    session_id = created.json()["id"]
    for text in ("I am agree", "I am agree with you"):
        res = await client.post(
            f"{BASE}/sessions/{session_id}/messages", headers=auth_headers, json={"text": text}
        )
        assert res.status_code == 200

    memory = (await client.get(f"{BASE}/memory", headers=auth_headers)).json()
    agree = next(item for item in memory if item["memory_key"] == "agree_without_be")
    assert agree["occurrence_count"] == 2


async def test_session_is_private_to_owner(client: AsyncClient, auth_headers: dict[str, str]) -> None:
    created = await client.post(
        f"{BASE}/sessions",
        headers=auth_headers,
        json={"target_language_code": "sr", "cefr_level": "A1", "personality": "professional"},
    )
    session_id = created.json()["id"]

    payload = {"email": "other@example.com", "password": "supersecret123!", "full_name": "Other"}
    assert (await client.post("/api/v1/auth/register", json=payload)).status_code == 201
    login = await client.post("/api/v1/auth/login", json={"email": payload["email"], "password": payload["password"]})
    other_headers = {"Authorization": f"Bearer {login.json()['access_token']}"}

    assert (await client.get(f"{BASE}/sessions/{session_id}", headers=other_headers)).status_code == 404
    assert (
        await client.post(
            f"{BASE}/sessions/{session_id}/messages", headers=other_headers, json={"text": "Zdravo"}
        )
    ).status_code == 404


async def test_tutor_stats_summarize_activity(client: AsyncClient, auth_headers: dict[str, str]) -> None:
    created = await client.post(
        f"{BASE}/sessions",
        headers=auth_headers,
        json={"target_language_code": "en", "cefr_level": "A2", "personality": "patient"},
    )
    session_id = created.json()["id"]
    for text in ("I am agree", "I am agree with you"):
        response = await client.post(
            f"{BASE}/sessions/{session_id}/messages",
            headers=auth_headers,
            json={"text": text},
        )
        assert response.status_code == 200

    response = await client.get(f"{BASE}/stats", headers=auth_headers)
    assert response.status_code == 200
    stats = response.json()
    assert stats["total_sessions"] == 1
    assert stats["total_user_messages"] == 2
    assert stats["total_corrections"] == 2
    assert stats["memory_patterns"] >= 1
    assert stats["repeated_patterns"] >= 1
    assert stats["sessions_last_7_days"] == 1
    assert stats["most_frequent_category"] == "grammar"
    assert stats["most_frequent_pattern"] == "agree_without_be"
