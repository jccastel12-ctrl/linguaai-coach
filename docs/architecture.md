# Arquitectura

## Visión general

```
┌──────────────┐   HTTPS/JSON    ┌──────────────────┐   SQL    ┌──────────────┐
│  Navegador   │ ──────────────▶ │  API (FastAPI)   │ ───────▶ │ PostgreSQL   │
│  Next.js UI  │                 │  /api/v1/*       │          └──────────────┘
└──────┬───────┘                 │  /health         │   (opc.) ┌──────────────┐
       │ SSR (API_INTERNAL_URL)  └──────────────────┘ ───────▶ │ Redis        │
┌──────▼───────┐                                               └──────────────┘
│ Next.js srv  │ ──────────────────────▲
└──────────────┘
```

- **Web (`apps/web`)**: Next.js App Router. Los Server Components llaman a la API usando `API_INTERNAL_URL` (red interna de Docker); el navegador usa `NEXT_PUBLIC_API_URL`.
- **API (`apps/api`)**: monolito modular. Un único despliegue, pero el código se organiza por **dominios** con límites claros para poder extraer servicios en el futuro si es necesario.
- **PostgreSQL**: fuente de verdad. Esquema versionado con Alembic.
- **Redis** (opcional): reservado para rate limiting, caché y colas de tareas de IA.

## API: organización por dominios

```
app/
├── core/            # Transversal: config, database, security, health, constants
├── domains/
│   ├── auth/        # registro, login, emisión/validación de JWT, dependencia CurrentUser
│   ├── users/       # User, StudentProfile, UserLanguage
│   ├── languages/   # catálogo de idiomas (es, en, sr)
│   └── lessons/     # Lesson, LessonProgress
├── models.py        # Registro de todos los modelos (Alembic/tests)
└── main.py          # create_app(): middlewares, routers
```

Cada dominio sigue la misma estructura:

| Archivo | Responsabilidad |
|---------|-----------------|
| `models.py` | Modelos ORM (SQLAlchemy 2.0, tipado con `Mapped`) |
| `schemas.py` | Contratos de entrada/salida (Pydantic v2) |
| `service.py` | Lógica de negocio; recibe una `Session`, sin conocer HTTP |
| `router.py` | Endpoints HTTP; traduce errores de dominio a códigos HTTP |

Reglas: los routers no contienen SQL; los servicios no lanzan `HTTPException`; un dominio puede usar el `service` de otro, nunca su `router`.

## Modelo de datos (migración `001`)

```
languages (code PK)                 users (id UUID PK, email único)
   ▲   ▲   ▲                          │ 1
   │   │   │                          ├──1 student_profiles (native_language_code → languages)
   │   │   └──── user_languages ◀─────┤ N  (cefr_level A1..C2, is_primary, único user+idioma)
   │   │                              │
   │   └──── lessons (language_code, slug único por idioma, cefr_level, content JSON, is_published)
   │              ▲
   │              └──── lesson_progress ◀── users (status, score 0..100, único user+lección)
```

Decisiones del esquema:

- **UUID** como PK de entidades de negocio (no enumerables); código ISO 639-1 como PK natural de `languages`.
- **Niveles MCER (CEFR)** y estados de progreso validados con `CHECK` en la BD además de en Pydantic.
- **Convención de nombres** de constraints (`pk_`, `fk_`, `uq_`, `ck_`, `ix_`) para migraciones deterministas.
- `lessons.content` en JSON con campo `version` interno: permite evolucionar el formato de ejercicios sin migraciones frecuentes.
- `ON DELETE CASCADE` desde `users` (borrado de cuenta / RGPD); `RESTRICT` sobre `languages` para no perder contenido.
- Los idiomas de lanzamiento se insertan en la propia migración (datos de referencia); las lecciones de ejemplo, con `make seed` (solo desarrollo).

## Autenticación

1. `POST /auth/register` → hash Argon2id, crea `User` + `StudentProfile`.
2. `POST /auth/login` → JWT de acceso (`sub`=user id, `exp`, `iat`, `type=access`), 30 min por defecto.
3. `CurrentUser` (dependencia) valida firma, expiración, tipo y que el usuario siga activo.

Pendiente: refresh tokens con rotación, verificación de email, recuperación de contraseña, rate limiting (Redis).

## Contratos compartidos

`packages/shared-types` contiene las interfaces TypeScript que reflejan los esquemas Pydantic. La web las importa vía `@/types`. Plan: generarlas automáticamente desde `/openapi.json` (ver ADR-001).

## Futuro: módulo de IA

Se añadirá como dominio `app/domains/coach/` detrás de una interfaz `LLMProvider` (sin acoplar a un proveedor concreto), con tareas largas ejecutadas en workers vía Redis.

## Capa comercial v0.9

El dominio `billing` mantiene separado el acceso comercial de la lógica pedagógica. `subscriptions` define el tier actual (`basic` o `pro`) y `usage_events` registra acciones exitosas medibles. Tutor, traducción y pronunciación consultan la cuota antes de procesar y registran consumo después de una respuesta exitosa.

No existe todavía integración con un procesador de pagos. `requested_plan` captura intención de upgrade sin activar Pro. Cuando se incorpore checkout, el cambio de plan debe ocurrir únicamente después de un evento verificable del proveedor de pagos (webhook firmado), no desde el navegador del usuario.

## Administración y facturación (v1.0)

La API incorpora un dominio `admin` separado de la experiencia del estudiante. Todo endpoint administrativo depende de un usuario autenticado con `is_superuser=true`; la web no decide permisos por sí sola.

Los cambios manuales de suscripción se registran en `billing_audit_events`. La tabla `subscriptions` mantiene el derecho de acceso (`plan_tier`, `status`) y reserva campos neutrales para sincronizar en el futuro un proveedor externo. Checkout y webhooks permanecen deshabilitados en v1.0: la preparación del modelo no equivale a una integración de pagos.
