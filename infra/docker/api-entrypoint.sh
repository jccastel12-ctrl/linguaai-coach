#!/bin/sh
# Applies pending migrations (unless disabled) and then runs the given command.
set -e

if [ "${RUN_MIGRATIONS_ON_START:-true}" = "true" ]; then
  echo "[entrypoint] Running database migrations..."
  alembic upgrade head
fi

exec "$@"
