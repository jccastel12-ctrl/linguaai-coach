#!/bin/sh
set -eu

ENV_FILE="${1:-.env.production}"
[ -f "$ENV_FILE" ] || { echo "ERROR: no existe $ENV_FILE" >&2; exit 1; }
set -a
# shellcheck disable=SC1090
. "$ENV_FILE"
set +a

APP_URL="${APP_PUBLIC_URL:?APP_PUBLIC_URL is required}"
API_URL="${NEXT_PUBLIC_API_URL:?NEXT_PUBLIC_API_URL is required}"

check() {
  label="$1"
  url="$2"
  echo "[smoke] $label -> $url"
  code=$(curl -L -sS -o /tmp/linguaai-smoke-body -w "%{http_code}" --connect-timeout 10 --max-time 20 "$url" || true)
  case "$code" in
    200|204|301|302|307|308) echo "  OK ($code)" ;;
    *) echo "  FAIL ($code)" >&2; cat /tmp/linguaai-smoke-body >&2 2>/dev/null || true; exit 1 ;;
  esac
}

check "web" "$APP_URL/"
check "api liveness" "$API_URL/health"
check "api readiness" "$API_URL/health/ready"

echo "Smoke test OK."
