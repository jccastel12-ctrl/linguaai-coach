#!/bin/sh
set -eu

ENV_FILE="${1:-.env.production}"
BACKUP_FILE="${2:-}"
[ -n "$BACKUP_FILE" ] || { echo "Uso: $0 .env.production backups/archivo.dump" >&2; exit 1; }
[ -f "$ENV_FILE" ] || { echo "ERROR: no existe $ENV_FILE" >&2; exit 1; }
[ -f "$BACKUP_FILE" ] || { echo "ERROR: no existe $BACKUP_FILE" >&2; exit 1; }

if [ "${CONFIRM_RESTORE:-}" != "YES" ]; then
  echo "RESTORE CANCELADO. Esta operación reemplaza objetos de la base." >&2
  echo "Ejecuta con CONFIRM_RESTORE=YES si verificaste el backup y el destino." >&2
  exit 1
fi

docker compose --env-file "$ENV_FILE" -f compose.production.yml exec -T postgres \
  sh -c 'pg_restore -U "$POSTGRES_USER" -d "$POSTGRES_DB" --clean --if-exists --no-owner' < "$BACKUP_FILE"

echo "Restauración finalizada."
