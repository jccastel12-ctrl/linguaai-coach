"""Runs Alembic upgrade/downgrade against a temporary SQLite file to validate migrations.

The alembic/env.py converts +asyncpg → +psycopg and +aiosqlite → +pysqlite so that
Alembic can use its standard synchronous engine even though the app uses asyncpg at runtime.
A sqlite+pysqlite URL (used here) passes through the converter unchanged.

CI additionally runs `alembic upgrade head` against a real PostgreSQL service.
"""

from pathlib import Path

import pytest
from sqlalchemy import create_engine, inspect, text

from alembic import command
from alembic.config import Config

API_DIR = Path(__file__).resolve().parents[2]


@pytest.fixture()
def alembic_cfg(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> tuple[Config, str]:
    url = f"sqlite+pysqlite:///{tmp_path / 'migrations.db'}"
    # env.py reads the URL from settings; patch the cached settings instance.
    from app.core.config import settings

    monkeypatch.setattr(settings, "database_url", url)
    cfg = Config(str(API_DIR / "alembic.ini"))
    cfg.set_main_option("script_location", str(API_DIR / "alembic"))
    return cfg, url


def test_upgrade_and_downgrade(alembic_cfg: tuple[Config, str]) -> None:
    cfg, url = alembic_cfg
    command.upgrade(cfg, "head")
    engine = create_engine(url)
    tables = set(inspect(engine).get_table_names())
    assert {
        "languages",
        "users",
        "student_profiles",
        "user_languages",
        "lessons",
        "lesson_progress",
        "tutor_sessions",
        "tutor_turns",
        "learning_memories",
        "pronunciation_attempts",
        "subscriptions",
        "usage_events",
        "billing_audit_events",
    } <= tables
    with engine.connect() as conn:
        codes = {row[0] for row in conn.execute(text("SELECT code FROM languages"))}
    assert codes == {"es", "en", "sr"}

    command.downgrade(cfg, "base")
    assert "users" not in inspect(engine).get_table_names()
    engine.dispose()
