# Guía de desarrollo

## Requisitos

| Herramienta | Versión |
|-------------|---------|
| Docker + Compose v2 | 24+ |
| Python | 3.11+ (la imagen usa 3.12) |
| Node.js | 20.9+ (requerido por Next.js 15) |
| make | cualquiera |

## Opción A — Todo en Docker (recomendado)

```bash
cp .env.example .env        # cambia POSTGRES_PASSWORD y SECRET_KEY
make up                     # construye y levanta postgres, api y web
make logs                   # sigue los logs
make seed                   # lecciones de ejemplo
```

- La API se recarga al editar `apps/api/` (volumen montado + `uvicorn --reload`).
- La web se recarga al editar `apps/web/src/` y `packages/shared-types/src/`.
- Las migraciones se aplican automáticamente al arrancar la API (`RUN_MIGRATIONS_ON_START=true`).
- Si cambias dependencias (`requirements*.txt` o `package.json`), ejecuta `make build`.

## Opción B — Procesos locales

```bash
make install                                   # venv en apps/api/.venv + npm install
cp apps/api/.env.example apps/api/.env         # apunta DATABASE_URL a tu Postgres
cp apps/web/.env.local.example apps/web/.env.local

# Solo la base de datos en Docker:
docker compose up -d postgres

cd apps/api && .venv/bin/alembic upgrade head && cd -
make api-dev        # http://localhost:8000/docs
make web-dev        # http://localhost:3000
```

## Tests y calidad

```bash
make test-api       # pytest — usa SQLite en memoria, no necesita Postgres
make lint           # ruff check + ruff format --check + eslint
make typecheck      # tsc en web y shared-types
make format         # autoformatea Python
```

Los tests de la API:

- `test_health.py` — liveness, readiness y cabeceras de seguridad.
- `test_users.py` — registro, normalización de email, duplicados, contraseña débil, login, `/users/me`, perfil e idiomas.
- `test_languages_lessons.py` — catálogo, filtrado de lecciones publicadas, progreso.
- `test_migrations.py` — `alembic upgrade head` / `downgrade base` sobre SQLite temporal.

La CI además ejecuta las migraciones contra **PostgreSQL real**.

## Migraciones (Alembic)

```bash
# 1. Modifica/crea modelos en app/domains/<dominio>/models.py
# 2. Si es un modelo nuevo, impórtalo en app/models.py
make migration m="add vocabulary table"
# 3. REVISA el archivo generado en apps/api/alembic/versions/
make migrate
```

Reglas:

- Nunca edites una migración ya aplicada en un entorno compartido; crea una nueva.
- Toda migración debe tener `downgrade()` funcional.
- `alembic check` debe reportar "No new upgrade operations detected" tras migrar.

## Añadir un nuevo dominio

1. Crear `app/domains/<nombre>/` con `__init__.py`, `models.py`, `schemas.py`, `service.py`, `router.py`.
2. Registrar los modelos en `app/models.py`.
3. Registrar el router en `app/main.py`.
4. Añadir los tipos correspondientes en `packages/shared-types/src/index.ts`.
5. Tests en `app/tests/test_<nombre>.py`.

## Convenciones

- **Python**: Ruff (line-length 120), tipado completo, SQLAlchemy 2.0 estilo `select()`.
- **TypeScript**: `strict`, imports con alias `@/`, sin `any`.
- **Commits**: [Conventional Commits](https://www.conventionalcommits.org/es/) (`feat:`, `fix:`, `docs:`...).
- **Ramas**: `main` protegida; trabajo en `feat/*`, `fix/*` con PR y CI verde.
- **Idioma**: documentación en español; código e identificadores en inglés.

## Problemas frecuentes

| Síntoma | Solución |
|---------|----------|
| `POSTGRES_PASSWORD` required al hacer `make up` | Falta `.env`: `cp .env.example .env` |
| La web muestra "Sin conexión" | Revisa `make logs` de `api` y `curl localhost:8000/health` |
| Puerto 5432 ocupado | Cambia `POSTGRES_PORT` en `.env` |
| `ValueError: SECRET_KEY must be set...` | Estás en `ENVIRONMENT=staging/production`; genera un secreto real |

## Crear un administrador local

Primero registra una cuenta normal desde la web o API. Luego, con el stack Docker activo:

```bash
make promote-admin e="admin@dominio.com"
```

La cuenta podrá acceder a `/admin`. No existe una contraseña administrativa predeterminada ni se crean superusuarios automáticamente.
