# Despliegue de LinguaAI Coach v1.2

Esta guía prepara un despliegue inicial en un servidor Linux con Docker Compose. No obliga a usar este proveedor: el mismo `api.Dockerfile` y `web.Dockerfile` pueden desplegarse después en servicios administrados.

## Arquitectura de referencia

- `Caddy`: termina HTTPS y renueva certificados TLS automáticamente.
- `web`: Next.js standalone, accesible solo a través de Caddy.
- `api`: FastAPI, accesible solo a través de Caddy y de la red interna.
- `postgres`: PostgreSQL 16, sin puerto público.

Se recomiendan dos DNS:

- `app.tudominio.com` → interfaz web.
- `api.tudominio.com` → API.

## 1. Preparación

En el servidor:

```bash
cp .env.production.example .env.production
chmod 600 .env.production
```

Edita todos los valores `change-me`. Genera secretos con herramientas del sistema, por ejemplo:

```bash
openssl rand -hex 32
python3 -c 'import secrets; print(secrets.token_urlsafe(48))'
```

No guardes `.env.production` en Git.

## 2. DNS y firewall

Antes de iniciar Caddy, crea registros A/AAAA para `APP_DOMAIN` y `API_DOMAIN` que apunten al servidor. Expón únicamente 80/tcp, 443/tcp y, si deseas HTTP/3, 443/udp. PostgreSQL, API y web no publican puertos directamente.

## 3. Preflight

```bash
./scripts/preflight-production.sh .env.production
```

También puedes ejecutar:

```bash
make prod-preflight
```

El preflight detecta secretos de ejemplo, HTTP sin TLS, wildcard CORS y otras configuraciones inseguras obvias.

## 4. Build y migraciones

```bash
make prod-build
make prod-migrate
```

Las migraciones se ejecutan como una tarea única antes de levantar réplicas. `RUN_MIGRATIONS_ON_START=false` evita carreras entre instancias.

## 5. Arranque

```bash
make prod-up
make prod-ps
```

Caddy solicitará certificados públicos. Si DNS todavía no resuelve al servidor, el TLS automático fallará hasta corregirlo.

## 6. Verificación

```bash
make prod-smoke
```

Comprueba web, liveness y readiness. Después revisa manualmente registro, login, tutor, traductor y pronunciación desde un navegador compatible.

## 7. Backups

```bash
make prod-backup
```

Los backups manuales se crean en `backups/` y esta carpeta debe copiarse fuera del servidor. En producción comercial se recomienda además un PostgreSQL administrado con snapshots y PITR.

Restaurar requiere una confirmación explícita:

```bash
CONFIRM_RESTORE=YES ./scripts/restore-postgres.sh .env.production backups/linguaai-AAAAMMDDTHHMMSSZ.dump
```

Prueba el proceso de restauración en staging antes de depender de él.

## 8. Actualización de versión

1. Haz backup o confirma que el snapshot/PITR está sano.
2. Obtén la nueva versión del código.
3. Ejecuta `make prod-build`.
4. Ejecuta `make prod-migrate`.
5. Ejecuta `make prod-up`.
6. Ejecuta `make prod-smoke`.
7. Revisa logs: `make prod-logs`.

## Límites de esta entrega

- No configura un proveedor cloud, IP, dominio ni DNS reales.
- No activa Stripe.
- No incluye un proveedor SMTP; solo deja el contrato de variables preparado.
- No reemplaza backups externos administrados.
- No configura observabilidad externa (Sentry, OpenTelemetry, Prometheus).
