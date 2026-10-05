"""Test fixtures: isolated in-memory async SQLite DB per test, httpx AsyncClient with overridden get_db.

Uses aiosqlite (async SQLite) so the test DB driver matches the async SQLAlchemy session used in production.
pytest-asyncio is configured in asyncio_mode = "auto" (pyproject.toml) so all async fixtures/tests run
without needing explicit @pytest.mark.asyncio decorators.
"""

import os

os.environ.setdefault("ENVIRONMENT", "test")
os.environ.setdefault("DATABASE_URL", "sqlite+aiosqlite:///:memory:")

from collections.abc import AsyncGenerator  # noqa: E402

import pytest  # noqa: E402
from httpx import ASGITransport, AsyncClient  # noqa: E402
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine  # noqa: E402
from sqlalchemy.pool import StaticPool  # noqa: E402

from app.core.constants import SUPPORTED_LANGUAGES  # noqa: E402
from app.core.database import get_db  # noqa: E402
from app.main import app  # noqa: E402
from app.models import Base, Language, Lesson  # noqa: E402


@pytest.fixture()
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    TestingSession = async_sessionmaker(engine, expire_on_commit=False)

    async with TestingSession() as session:
        session.add_all(Language(**lang) for lang in SUPPORTED_LANGUAGES)
        session.add_all(
            [
                Lesson(
                    language_code="sr",
                    slug="pozdravi",
                    title="Pozdravi",
                    cefr_level="A1",
                    is_published=True,
                    content={"version": 1},
                ),
                Lesson(
                    language_code="sr",
                    slug="draft",
                    title="Draft",
                    cefr_level="A2",
                    is_published=False,
                    content={},
                ),
            ]
        )
        await session.commit()
        yield session

    await engine.dispose()


@pytest.fixture()
async def client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    async def override_get_db() -> AsyncGenerator[AsyncSession, None]:
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture()
async def auth_headers(client: AsyncClient) -> dict[str, str]:
    payload = {"email": "ana@example.com", "password": "supersecret123!", "full_name": "Ana"}
    assert (await client.post("/api/v1/auth/register", json=payload)).status_code == 201
    res = await client.post("/api/v1/auth/login", json={"email": payload["email"], "password": payload["password"]})
    return {"Authorization": f"Bearer {res.json()['access_token']}"}


@pytest.fixture()
async def admin_headers(client: AsyncClient, db_session: AsyncSession) -> dict[str, str]:
    payload = {"email": "admin@example.com", "password": "supersecret123!", "full_name": "Admin"}
    assert (await client.post("/api/v1/auth/register", json=payload)).status_code == 201
    from sqlalchemy import select
    from app.domains.users.models import User

    user = await db_session.scalar(select(User).where(User.email == payload["email"]))
    assert user is not None
    user.is_superuser = True
    await db_session.commit()
    res = await client.post("/api/v1/auth/login", json={"email": payload["email"], "password": payload["password"]})
    assert res.status_code == 200
    return {"Authorization": f"Bearer {res.json()['access_token']}"}
