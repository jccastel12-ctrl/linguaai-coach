"""Application settings loaded from environment variables (12-factor)."""

from functools import lru_cache
from typing import Literal

from pydantic import Field, SecretStr, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

INSECURE_DEFAULT_SECRET = "dev-only-insecure-secret-change-me"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "LinguaAI Coach API"
    app_version: str = "1.5.0"
    environment: Literal["development", "test", "staging", "production"] = "development"
    debug: bool = False
    api_v1_prefix: str = "/api/v1"

    database_url: str = "postgresql+asyncpg://linguaai:linguaai@localhost:5432/linguaai"
    redis_url: str | None = None

    secret_key: SecretStr = SecretStr(INSECURE_DEFAULT_SECRET)
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = Field(default=30, ge=1, le=1440)

    # Tutor provider. Keep this separate from translation so the translator can
    # use Azure while the tutor remains on the free deterministic provider.
    ai_provider: Literal["rule_based", "openai_compatible"] = "rule_based"
    ai_api_key: SecretStr | None = None
    ai_base_url: str = "https://api.openai.com/v1"
    ai_model: str = ""
    ai_timeout_seconds: int = Field(default=30, ge=5, le=120)

    # Translation provider. None preserves the historical behavior and follows
    # AI_PROVIDER (rule_based/openai_compatible). Azure is translation-only.
    translation_provider: Literal["rule_based", "openai_compatible", "azure_translator"] | None = None
    azure_translator_key: SecretStr | None = None
    azure_translator_region: str | None = None
    azure_translator_endpoint: str = "https://api.cognitive.microsofttranslator.com"

    # Payment integration is deliberately disabled in v1.0. These fields reserve
    # the configuration contract needed for a future Stripe checkout/webhook adapter.
    payment_provider: Literal["disabled", "stripe"] = "disabled"
    stripe_secret_key: SecretStr | None = None
    stripe_webhook_secret: SecretStr | None = None
    stripe_price_id_pro: str | None = None
    app_public_url: str = "http://localhost:3000"

    # Transactional email. Use console only for local development.
    email_delivery_mode: Literal["disabled", "console", "smtp"] = "disabled"
    email_from: str | None = None
    smtp_host: str | None = None
    smtp_port: int = Field(default=587, ge=1, le=65535)
    smtp_username: str | None = None
    smtp_password: SecretStr | None = None
    smtp_starttls: bool = True

    # Comma-separated list of allowed origins, e.g. "http://localhost:3000,https://app.example.com"
    cors_origins: str = "http://localhost:3000"

    @field_validator("database_url", mode="before")
    @classmethod
    def _normalize_database_url(cls, value: object) -> object:
        """Accept managed-Postgres URLs while keeping the app on asyncpg."""
        if not isinstance(value, str):
            return value
        if value.startswith("postgres://"):
            return "postgresql+asyncpg://" + value[len("postgres://") :]
        if value.startswith("postgresql://"):
            return "postgresql+asyncpg://" + value[len("postgresql://") :]
        return value

    @property
    def cors_origins_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]

    @property
    def is_production(self) -> bool:
        return self.environment in ("staging", "production")

    @property
    def effective_translation_provider(self) -> str:
        return self.translation_provider or self.ai_provider

    @model_validator(mode="after")
    def _validate_security(self) -> "Settings":
        if self.is_production:
            secret = self.secret_key.get_secret_value()
            if secret == INSECURE_DEFAULT_SECRET or len(secret) < 32:
                raise ValueError("SECRET_KEY must be set to a random value of >= 32 chars outside development")
            if self.debug:
                raise ValueError("DEBUG must be false outside development")
            if "*" in self.cors_origins_list:
                raise ValueError("Wildcard CORS origins are not allowed outside development")
            if self.email_delivery_mode == "console":
                raise ValueError("EMAIL_DELIVERY_MODE=console is not allowed outside development")
        return self


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
