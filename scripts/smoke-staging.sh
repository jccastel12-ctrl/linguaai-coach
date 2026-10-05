#!/usr/bin/env bash
set -euo pipefail

WEB_URL="${1:-}"
API_URL="${2:-}"

if [[ -z "$WEB_URL" || -z "$API_URL" ]]; then
  echo "Uso: ./scripts/smoke-staging.sh https://<web>.onrender.com https://<api>.onrender.com" >&2
  exit 2
fi

WEB_URL="${WEB_URL%/}"
API_URL="${API_URL%/}"

echo ">> Web: $WEB_URL"
curl --fail --silent --show-error --location --max-time 90 "$WEB_URL/" >/dev/null
echo "OK /"

echo ">> API: $API_URL"
curl --fail --silent --show-error --location --max-time 90 "$API_URL/health" | grep -q '"status"'
echo "OK /health"
curl --fail --silent --show-error --location --max-time 90 "$API_URL/health/ready" | grep -q '"status"'
echo "OK /health/ready"

echo ">> Smoke staging completado."
