# LinguaAI Coach v1.2.0 — Preparación de despliegue

## Añadido

- `compose.production.yml` con PostgreSQL privado, API FastAPI, web Next.js y Caddy.
- HTTPS automático mediante Caddy para dominio web y dominio API separados.
- `.env.production.example` sin secretos reales.
- `scripts/preflight-production.sh` para detectar configuración insegura antes del despliegue.
- `scripts/smoke-production.sh` para verificar web, liveness y readiness después de publicar.
- Scripts de backup y restauración de PostgreSQL con confirmación explícita.
- Comandos `make prod-*` para build, migración, arranque, logs, smoke test y backup.
- `docs/deployment.md` con procedimiento completo de despliegue.
- `docs/release-checklist.md` para revisión técnica, de seguridad, producto y legal.

## Decisiones

- Las migraciones de producción se ejecutan como tarea única; las réplicas usan `RUN_MIGRATIONS_ON_START=false`.
- PostgreSQL no publica puerto en producción.
- API y web no publican puertos directos; Caddy es el único punto de entrada.
- Pagos continúan desactivados.
- La entrega es independiente de proveedor cloud: puede ejecutarse en un VPS con Docker y sirve como base para migrar luego a servicios administrados.
