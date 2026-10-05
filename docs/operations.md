# Operaciones

> Este documento describe la base operativa. El scaffold **no incluye** aún infraestructura de producción (IaC, dominio, TLS); se definirá en un ADR posterior.

## Entornos

| Entorno | `ENVIRONMENT` | Notas |
|---------|---------------|-------|
| Local | `development` | Docker Compose; secretos de ejemplo permitidos |
| CI | `test` | SQLite en memoria + Postgres de servicio para migraciones |
| Staging | `staging` | Igual que producción, datos ficticios |
| Producción | `production` | Validaciones de seguridad estrictas al arrancar |

En `staging`/`production` la API **falla al arrancar** si: `SECRET_KEY` es la de desarrollo o tiene < 32 caracteres, `DEBUG=true`, o `CORS_ORIGINS` contiene `*`. Además se ocultan `/docs`, `/redoc` y `/openapi.json`.

## Variables de entorno

| Variable | Servicio | Obligatoria en prod | Descripción |
|----------|----------|---------------------|-------------|
| `DATABASE_URL` | api | sí | `postgresql+psycopg://user:pass@host:5432/db` |
| `SECRET_KEY` | api | sí | Firma de JWT, ≥ 32 caracteres aleatorios |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | api | no | Por defecto 30 |
| `CORS_ORIGINS` | api | sí | Orígenes separados por comas |
| `REDIS_URL` | api | no | Reservado para rate limiting/colas |
| `RUN_MIGRATIONS_ON_START` | api | no | `true` en local; en prod se recomienda `false` y migrar como paso del despliegue |
| `NEXT_PUBLIC_API_URL` | web | sí | URL pública de la API (se incrusta en el build) |
| `API_INTERNAL_URL` | web | no | URL interna para SSR |

Los secretos deben gestionarse con el gestor del proveedor (AWS Secrets Manager, GCP Secret Manager, Doppler, etc.), nunca en archivos versionados.

## Imágenes de producción

```bash
docker build -f infra/docker/api.Dockerfile --target prod -t linguaai-api:<versión> .
docker build -f infra/docker/web.Dockerfile --target prod \
  --build-arg NEXT_PUBLIC_API_URL=https://api.ejemplo.com -t linguaai-web:<versión> .
```

- Ambas imágenes ejecutan con usuario no-root.
- La web usa `output: "standalone"` (servidor Node mínimo).
- `NEXT_PUBLIC_*` se resuelve en tiempo de build: pásalo con `--build-arg NEXT_PUBLIC_API_URL=...` (el `ARG` ya existe en `web.Dockerfile`).

## Despliegue (orden recomendado)

1. Construir y publicar imágenes etiquetadas con el SHA del commit.
2. Ejecutar migraciones como tarea única: `alembic upgrade head` (con `RUN_MIGRATIONS_ON_START=false` en los réplicas).
3. Desplegar la API (rolling update) y esperar a que `/health/ready` devuelva 200.
4. Desplegar la web.

Las migraciones deben ser **compatibles hacia atrás** (expand → migrate → contract) para permitir rolling updates.

## Health checks

| Endpoint | Uso | Comportamiento |
|----------|-----|----------------|
| `GET /health` | liveness | 200 si el proceso responde; no toca dependencias |
| `GET /health/ready` | readiness | 200 si la BD responde a `SELECT 1`, 503 si no |

## Base de datos

- **Backups**: snapshots diarios gestionados + PITR (point-in-time recovery) en producción. Probar la restauración al menos trimestralmente.
- Backup manual local:
  ```bash
  docker compose exec postgres sh -c 'pg_dump -U $POSTGRES_USER -d $POSTGRES_DB -Fc' > backup.dump
  ```
- Restauración local:
  ```bash
  docker compose exec -T postgres sh -c 'pg_restore -U $POSTGRES_USER -d $POSTGRES_DB --clean' < backup.dump
  ```
- Rollback de esquema: `alembic downgrade -1` (solo si la migración es reversible sin pérdida de datos).

## Observabilidad (pendiente)

- Logs estructurados en JSON con `request_id`.
- Métricas (Prometheus/OpenTelemetry) y trazas distribuidas.
- Error tracking (p. ej. Sentry) con depuración de PII.
- Alertas: tasa de 5xx, latencia p95, readiness fallido, conexiones a BD.

## Seguridad operativa

- Rotación de `SECRET_KEY` invalida todos los tokens: planificar ventana o soportar múltiples claves (pendiente).
- TLS terminado en el balanceador; HSTS en la web.
- Escaneo de dependencias (Dependabot/Renovate) y de imágenes (Trivy) en CI — pendiente.
- Datos personales (email, perfil, progreso) sujetos a RGPD: borrado de cuenta en cascada ya soportado por el esquema.

## Operación administrativa v1.0

- No existe un usuario administrador por defecto.
- Registra primero una cuenta normal y promuévela explícitamente con `make promote-admin e="correo@dominio.com"`.
- Todo cambio Basic/Pro manual queda en `billing_audit_events`.
- `PAYMENT_PROVIDER=disabled` es el valor seguro de lanzamiento del MVP. No configures una pasarela real hasta implementar checkout, validación de webhook, idempotencia y reconciliación.


## Despliegue de referencia v1.2

Para el stack de producción Docker Compose + Caddy, consulta `docs/deployment.md` y `docs/release-checklist.md`.
