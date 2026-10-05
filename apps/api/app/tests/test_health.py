from httpx import AsyncClient


async def test_health_returns_ok(client: AsyncClient) -> None:
    res = await client.get("/health")
    assert res.status_code == 200
    body = res.json()
    assert body["status"] == "ok"
    assert body["environment"] == "test"
    assert "version" in body


async def test_health_sets_security_headers(client: AsyncClient) -> None:
    res = await client.get("/health")
    assert res.headers["X-Content-Type-Options"] == "nosniff"
    assert res.headers["X-Frame-Options"] == "DENY"


async def test_readiness_checks_database(client: AsyncClient) -> None:
    res = await client.get("/health/ready")
    assert res.status_code == 200
    assert res.json() == {"status": "ok", "checks": {"database": "ok"}}
