#!/bin/sh
set -eu

ENV_FILE="${1:-.env.production}"
OUT_DIR="${2:-backups}"
[ -f "$ENV_FILE" ] || { echo "ERROR: no existe $ENV_FILE" >&2; exit 1; }
mkdir -p "$OUT_DIR"
stamp=$(date -u +%Y%m%dT%H%M%SZ)
out="$OUT_DIR/linguaai-$stamp.dump"

docker compose --env-file "$ENV_FILE" -f compose.production.yml exec -T postgres \
  sh -c 'pg_dump -U "$POSTGRES_USER" -d "$POSTGRES_DB" -Fc' > "$out"

echo "Backup creado: $out"
