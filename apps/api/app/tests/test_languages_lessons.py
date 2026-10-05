from httpx import AsyncClient


async def test_list_languages_includes_launch_languages(client: AsyncClient) -> None:
    res = await client.get("/api/v1/languages")
    assert res.status_code == 200
    assert {lang["code"] for lang in res.json()} == {"es", "en", "sr"}


async def test_get_unknown_language_returns_404(client: AsyncClient) -> None:
    assert (await client.get("/api/v1/languages/xx")).status_code == 404


async def test_lessons_only_published_are_listed(client: AsyncClient) -> None:
    res = await client.get("/api/v1/lessons", params={"language": "sr"})
    assert res.status_code == 200
    assert [lesson["slug"] for lesson in res.json()] == ["pozdravi"]


async def test_lesson_progress_flow(client: AsyncClient, auth_headers: dict[str, str]) -> None:
    lesson_id = (await client.get("/api/v1/lessons")).json()[0]["id"]
    res = await client.put(
        f"/api/v1/lessons/{lesson_id}/progress", headers=auth_headers, json={"status": "completed", "score": 90}
    )
    assert res.status_code == 200
    assert res.json()["completed_at"] is not None

    progress = (await client.get("/api/v1/lessons/progress/me", headers=auth_headers)).json()
    assert len(progress) == 1 and progress[0]["score"] == 90


async def test_lesson_progress_rejects_invalid_score(client: AsyncClient, auth_headers: dict[str, str]) -> None:
    lesson_id = (await client.get("/api/v1/lessons")).json()[0]["id"]
    res = await client.put(
        f"/api/v1/lessons/{lesson_id}/progress", headers=auth_headers, json={"status": "completed", "score": 150}
    )
    assert res.status_code == 422
