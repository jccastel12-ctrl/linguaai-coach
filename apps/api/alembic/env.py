"""Alembic environment. The database URL always comes from app settings (DATABASE_URL).

Alembic itself runs migrations synchronously; we convert async driver prefixes to their
sync equivalents so the same DATABASE_URL works for both the async application and for
Alembic CLI / migration tests.

  postgresql+asyncpg://...  →  postgresql+psycopg://...
  sqlite+aiosqlite://...    →  sqlite+pysqlite://...
"""

from logging.config import fileConfig

from sqlalchemy import engine_from_config, pool

from alembic import context
from app.core.config import settings
from app.models import Base

config = context.config

# Convert async driver prefix to synchronous equivalent.
_raw_url = settings.database_url.replace("%", "%%")
_sync_url = _raw_url.replace("+asyncpg", "+psycopg").replace("+aiosqlite", "+pysqlite")
config.set_main_option("sqlalchemy.url", _sync_url)

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    context.configure(
        url=config.get_main_option("sqlalchemy.url"),
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}), prefix="sqlalchemy.", poolclass=pool.NullPool
    )
    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
            render_as_batch=connection.dialect.name == "sqlite",
        )
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
