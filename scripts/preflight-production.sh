#!/bin/sh
set -eu

ENV_FILE="${1:-.env.production}"

if [ ! -f "$ENV_FILE" ]; then
  echo "ERROR: no existe $ENV_FILE" >&2
  echo "Copia .env.production.example a .env.production y completa los valores." >&2
  exit 1
fi

# Load KEY=VALUE pairs from the env file. The template intentionally avoids shell syntax.
set -a
# shellcheck disable=SC1090
. "$ENV_FILE"
set +a

fail=0
required="APP_DOMAIN API_DOMAIN ACME_EMAIL APP_PUBLIC_URL NEXT_PUBLIC_API_URL POSTGRES_USER POSTGRES_PASSWORD POSTGRES_DB DATABASE_URL SECRET_KEY CORS_ORIGINS"
for key in $required; do
  eval "value=\${$key:-}"
  if [ -z "$value" ]; then
    echo "ERROR: falta $key" >&2
    fail=1
  fi
done

if grep -Eq '^[A-Za-z_][A-Za-z0-9_]*=.*change-me' "$ENV_FILE"; then
  echo "ERROR: todavía existen valores de configuración con 'change-me' en $ENV_FILE" >&2
  fail=1
fi

if [ "${ENVIRONMENT:-}" != "production" ]; then
  echo "ERROR: ENVIRONMENT debe ser production" >&2
  fail=1
fi

if [ "${DEBUG:-false}" != "false" ]; then
  echo "ERROR: DEBUG debe ser false" >&2
  fail=1
fi

if [ "${RUN_MIGRATIONS_ON_START:-false}" != "false" ]; then
  echo "ERROR: RUN_MIGRATIONS_ON_START debe ser false en producción" >&2
  fail=1
fi

case "${APP_PUBLIC_URL:-}" in https://*) ;; *) echo "ERROR: APP_PUBLIC_URL debe usar https://" >&2; fail=1 ;; esac
case "${NEXT_PUBLIC_API_URL:-}" in https://*) ;; *) echo "ERROR: NEXT_PUBLIC_API_URL debe usar https://" >&2; fail=1 ;; esac


case "${DATABASE_URL:-}" in
  postgresql+asyncpg://*) ;;
  *) echo "ERROR: DATABASE_URL debe usar postgresql+asyncpg:// en producción" >&2; fail=1 ;;
esac

if [ "${APP_DOMAIN:-}" = "${API_DOMAIN:-}" ]; then
  echo "ERROR: APP_DOMAIN y API_DOMAIN deben ser distintos" >&2
  fail=1
fi

if [ "${CORS_ORIGINS:-}" = "*" ]; then
  echo "ERROR: CORS_ORIGINS no puede ser '*' en producción" >&2
  fail=1
fi

secret_len=$(printf %s "${SECRET_KEY:-}" | wc -c | tr -d ' ')
if [ "$secret_len" -lt 32 ]; then
  echo "ERROR: SECRET_KEY debe tener al menos 32 caracteres" >&2
  fail=1
fi

if [ "${EMAIL_DELIVERY_MODE:-disabled}" = "smtp" ]; then
  for key in EMAIL_FROM SMTP_HOST SMTP_USERNAME SMTP_PASSWORD; do
    eval "value=\${$key:-}"
    if [ -z "$value" ]; then
      echo "ERROR: $key es obligatorio cuando EMAIL_DELIVERY_MODE=smtp" >&2
      fail=1
    fi
  done
fi

if [ "${PAYMENT_PROVIDER:-disabled}" = "stripe" ]; then
  echo "ERROR: Stripe permanece deliberadamente deshabilitado en v1.2; no actives cobros antes de implementar checkout/webhooks." >&2
  fail=1
fi

if [ "$fail" -ne 0 ]; then
  exit 1
fi

echo "Preflight OK: variables mínimas de producción validadas."
echo "Siguiente paso: valida DNS para $APP_DOMAIN y $API_DOMAIN, luego ejecuta 'make prod-build'."
