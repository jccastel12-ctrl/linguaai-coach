from httpx import AsyncClient

BASE = "/api/v1/pronunciation"


async def test_pronunciation_requires_authentication(client: AsyncClient) -> None:
    response = await client.get(f"{BASE}/exercises?language_code=en&cefr_level=A1")
    assert response.status_code == 401


async def test_lists_exercises(client: AsyncClient, auth_headers: dict[str, str]) -> None:
    response = await client.get(f"{BASE}/exercises?language_code=en&cefr_level=A1", headers=auth_headers)
    assert response.status_code == 200
    body = response.json()
    assert len(body) == 3
    assert body[0]["language_code"] == "en"
    assert body[0]["cefr_level"] == "A1"


async def test_perfect_pronunciation_transcript_scores_high(client: AsyncClient, auth_headers: dict[str, str]) -> None:
    phrase = "Three small trees are near the street."
    response = await client.post(
        f"{BASE}/evaluate",
        headers=auth_headers,
        json={
            "language_code": "en",
            "cefr_level": "A1",
            "expected_text": phrase,
            "recognized_text": phrase,
            "focus_sound": "th",
        },
    )
    assert response.status_code == 201
    body = response.json()
    assert body["overall_score"] == 100
    assert body["missing_words"] == []
    assert body["extra_words"] == []


async def test_serbian_latin_and_cyrillic_are_comparable(client: AsyncClient, auth_headers: dict[str, str]) -> None:
    response = await client.post(
        f"{BASE}/evaluate",
        headers=auth_headers,
        json={
            "language_code": "sr",
            "cefr_level": "A1",
            "expected_text": "Zdravo, kako si danas?",
            "recognized_text": "Здраво како си данас",
        },
    )
    assert response.status_code == 201
    assert response.json()["overall_score"] >= 95


async def test_stats_reflect_attempts(client: AsyncClient, auth_headers: dict[str, str]) -> None:
    await client.post(
        f"{BASE}/evaluate",
        headers=auth_headers,
        json={
            "language_code": "es",
            "cefr_level": "A1",
            "expected_text": "Hola mucho gusto",
            "recognized_text": "Hola mucho gusto",
        },
    )
    response = await client.get(f"{BASE}/stats", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["total_attempts"] == 1
    assert response.json()["average_score"] == 100
