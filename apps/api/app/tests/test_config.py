import pytest
from pydantic import ValidationError

from app.core.config import Settings

STRONG_SECRET = "x" * 48


def test_production_rejects_default_secret() -> None:
    with pytest.raises(ValidationError, match="SECRET_KEY"):
        Settings(environment="production")


def test_production_rejects_debug_and_wildcard_cors() -> None:
    with pytest.raises(ValidationError, match="DEBUG"):
        Settings(environment="production", secret_key=STRONG_SECRET, debug=True)
    with pytest.raises(ValidationError, match="CORS"):
        Settings(environment="production", secret_key=STRONG_SECRET, cors_origins="*")


def test_production_accepts_secure_settings() -> None:
    s = Settings(environment="production", secret_key=STRONG_SECRET, cors_origins="https://a.com, https://b.com")
    assert s.is_production
    assert s.cors_origins_list == ["https://a.com", "https://b.com"]


def test_managed_postgres_url_is_normalized_for_async_sqlalchemy() -> None:
    s = Settings(database_url="postgresql://user:pass@db.example.com:5432/linguaai?sslmode=require")
    assert s.database_url == "postgresql+asyncpg://user:pass@db.example.com:5432/linguaai?sslmode=require"


def test_legacy_postgres_scheme_is_normalized_for_async_sqlalchemy() -> None:
    s = Settings(database_url="postgres://user:pass@db.example.com/linguaai")
    assert s.database_url == "postgresql+asyncpg://user:pass@db.example.com/linguaai"
