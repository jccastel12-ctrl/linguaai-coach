# LinguaAI Coach — API

API REST en FastAPI, organizada por dominios (`auth`, `users`, `billing`, `languages`, `lessons`, `tutor`, `translation`, `pronunciation`).

## Ejecutar localmente

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements-dev.txt
cp .env.example .env            # ajusta DATABASE_URL y SECRET_KEY
.venv/bin/alembic upgrade head
.venv/bin/uvicorn app.main:app --reload --port 8000
```

- Documentación interactiva: http://localhost:8000/docs
- Health: http://localhost:8000/health y http://localhost:8000/health/ready

## Tests y lint

```bash
.venv/bin/pytest           # SQLite en memoria, no requiere Postgres
.venv/bin/ruff check . && .venv/bin/ruff format --check .
```

## Estructura

```
app/
├── core/        config.py, database.py, security.py, health.py, constants.py
├── domains/     auth/ users/ billing/ languages/ lessons/ tutor/ translation/ pronunciation/
├── scripts/     seed.py (lecciones de ejemplo, solo desarrollo)
├── tests/
├── models.py    registro de modelos para Alembic
└── main.py      create_app()
alembic/versions/001_initial_schema.py
```

Ver [docs/architecture.md](../../docs/architecture.md) y [docs/development.md](../../docs/development.md).


## Traducción

`POST /api/v1/translate` requiere JWT y admite los pares entre `es`, `en` y `sr`. En desarrollo, `AI_PROVIDER=rule_based` permite probar frases frecuentes sin costo; para texto libre se usa `AI_PROVIDER=openai_compatible`.

## Planes y límites de uso

El dominio `billing` incorpora la estructura comercial inicial sin proveedor de pagos:

- `GET /api/v1/billing/plans` — catálogo Basic/Pro.
- `GET /api/v1/billing/me` — plan actual y consumo diario.
- `POST /api/v1/billing/me/request-upgrade` — registra interés en Pro sin activarlo.

Las operaciones exitosas de Tutor IA, Traducción y Pronunciación generan eventos de uso. Si el usuario alcanza su cuota diaria, la API responde `429 Too Many Requests`.

## v1.0 — administración

El dominio `admin` exige un usuario con `is_superuser=true`. Para promover una cuenta existente en desarrollo:

```bash
python -m app.scripts.promote_admin admin@dominio.com
```

Rutas principales: `/api/v1/admin/overview`, `/api/v1/admin/users`, `/api/v1/admin/audit`. Los cambios manuales de plan quedan registrados en `billing_audit_events`.

La capa de pagos sigue deshabilitada. `GET /api/v1/billing/payment-capabilities` informa el estado real; no se realizan cobros en v1.0.


## Seguridad de cuenta v1.1

Endpoints adicionales bajo `/api/v1/auth`:

- `POST /password/change` (autenticado)
- `POST /password-reset/request`
- `POST /password-reset/confirm`
- `POST /email-verification/request` (autenticado)
- `POST /email-verification/confirm`

El reset y la verificación usan tokens de un solo uso almacenados en forma de hash. Configure `EMAIL_DELIVERY_MODE` y SMTP mediante variables de entorno.
