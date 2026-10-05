# LinguaAI Coach

Plataforma SaaS de aprendizaje de idiomas asistida por IA. Idiomas de lanzamiento: **español**, **inglés** y **serbio** (alfabetos latino y cirílico).

> Estado: **MVP v1.4.0**. Incluye autenticación, onboarding, perfiles, tutor conversacional, historial, progreso, traductor ES/EN/SR, voz básica de navegador, práctica de pronunciación, avatar tutor ligero, planes Basic/Pro, panel administrativo y experiencia móvil instalable como PWA. El análisis acústico de fonemas, checkout/pagos reales, avatares 3D/fotorrealistas y una app nativa siguen en la hoja de ruta.

---

## Stack

| Capa | Tecnología |
|------|------------|
| Web | Next.js 15 (App Router) · React 19 · TypeScript estricto |
| API | FastAPI · Pydantic v2 · SQLAlchemy 2.0 · Alembic |
| Base de datos | PostgreSQL 16 |
| Caché / colas (opcional) | Redis 7 |
| Autenticación | JWT (HS256) + contraseñas con Argon2id |
| Calidad | Ruff, Pytest, ESLint, `tsc`, GitHub Actions |
| Local | Docker Compose + Makefile |

## Estructura del monorepo

```
linguaai-coach/
├── apps/
│   ├── api/                 # FastAPI modular por dominios
│   │   ├── alembic/         # Migraciones (001_initial_schema)
│   │   └── app/
│   │       ├── core/        # config, database, security, health
│   │       ├── domains/     # auth, admin, users, billing, languages, lessons, tutor, translation, pronunciation
│   │       ├── scripts/     # seed de desarrollo
│   │       └── tests/       # pytest
│   └── web/                 # Next.js (App Router)
│       └── src/{app,components/ui,lib,types}
├── packages/shared-types/   # Contratos TypeScript compartidos
├── infra/docker/            # Dockerfiles (dev/prod) y entrypoint
├── docs/                    # Arquitectura, desarrollo, operaciones, ADRs
├── .github/workflows/ci.yml # CI: lint + tests + build
├── docker-compose.yml
└── Makefile
```

## Inicio rápido (Docker)

Requisitos: Docker 24+ con Compose v2 y `make`.

```bash
cp .env.example .env
# Edita .env: cambia POSTGRES_PASSWORD y SECRET_KEY
#   python3 -c "import secrets; print(secrets.token_urlsafe(48))"
make up          # postgres + api + web (aplica migraciones al arrancar)
make seed        # opcional: lecciones de ejemplo
```

| Servicio | URL (en tu máquina) |
|----------|---------------------|
| Web | http://localhost:3000 |
| API | http://localhost:8000 |
| Documentación OpenAPI | http://localhost:8000/docs |
| Health check | http://localhost:8000/health · http://localhost:8000/health/ready |

Para incluir Redis: `make up-redis`. Para detener: `make down`.

## Desarrollo sin Docker

Requisitos: Python 3.11+, Node.js 20.9+, PostgreSQL 16 accesible.

```bash
make install                         # venv de la API + npm install (workspaces)
cp apps/api/.env.example apps/api/.env
cp apps/web/.env.local.example apps/web/.env.local
cd apps/api && .venv/bin/alembic upgrade head && cd -
make api-dev                         # http://localhost:8000
make web-dev                         # http://localhost:3000
```

Detalles en [docs/development.md](docs/development.md).

## Comandos útiles

| Comando | Descripción |
|---------|-------------|
| `make help` | Lista todos los comandos |
| `make up` / `make down` | Levantar / detener el stack |
| `make logs` | Logs de todos los servicios |
| `make migrate` | `alembic upgrade head` en el contenedor |
| `make migration m="..."` | Nueva migración autogenerada |
| `make seed` | Datos de ejemplo (solo desarrollo) |
| `make test` | Tests de la API + typecheck de la web |
| `make lint` | Ruff + ESLint |

## API (v1)

| Método | Ruta | Auth | Descripción |
|--------|------|------|-------------|
| GET | `/health` | — | Liveness |
| GET | `/health/ready` | — | Readiness (verifica la BD) |
| POST | `/api/v1/auth/register` | — | Registro (crea perfil de estudiante) |
| POST | `/api/v1/auth/login` | — | Login JSON → JWT |
| POST | `/api/v1/auth/token` | — | Flujo OAuth2 password (Swagger UI) |
| GET / PATCH | `/api/v1/users/me` | JWT | Usuario actual |
| PATCH | `/api/v1/users/me/profile` | JWT | Perfil de estudiante |
| PUT | `/api/v1/users/me/languages` | JWT | Idioma en aprendizaje + nivel MCER |
| GET | `/api/v1/languages` · `/{code}` | — | Catálogo de idiomas |
| GET | `/api/v1/lessons` · `/{id}` | — | Lecciones publicadas (filtros `language`, `level`) |
| GET | `/api/v1/lessons/progress/me` | JWT | Mi progreso |
| PUT | `/api/v1/lessons/{id}/progress` | JWT | Registrar progreso |
| POST | `/api/v1/tutor/sessions` | JWT | Crear sesión con idioma, nivel y personalidad |
| GET | `/api/v1/tutor/sessions` | JWT | Listar mis sesiones |
| GET | `/api/v1/tutor/sessions/{id}` | JWT | Sesión y turnos persistidos |
| POST | `/api/v1/tutor/sessions/{id}/messages` | JWT | Enviar texto y recibir corrección/respuesta |
| GET | `/api/v1/tutor/memory` | JWT | Patrones de aprendizaje y errores recurrentes |
| POST | `/api/v1/translate` | JWT | Traducción de texto ES/EN/SR |
| GET | `/api/v1/billing/payment-capabilities` | — | Estado de la capa de pagos (v1.0: deshabilitada) |
| GET | `/api/v1/admin/overview` | Admin | Métricas administrativas |
| GET | `/api/v1/admin/users` | Admin | Usuarios y solicitudes Pro |
| PATCH | `/api/v1/admin/users/{id}/subscription` | Admin | Cambio manual de plan |
| PATCH | `/api/v1/admin/users/{id}/active` | Admin | Activar/desactivar usuario |
| GET | `/api/v1/admin/audit` | Admin | Auditoría de cambios |

## Seguridad por defecto

- Sin secretos en el repositorio: solo archivos `.env.example` con marcadores `change-me`.
- La API **se niega a arrancar** en `staging`/`production` si `SECRET_KEY` es la de desarrollo o tiene < 32 caracteres, si `DEBUG=true` o si CORS usa `*`.
- Contraseñas con Argon2id; mitigación de enumeración de usuarios por tiempo en el login.
- Puertos de Docker publicados solo en `127.0.0.1`; contenedores con usuario no-root.
- Cabeceras de seguridad en API y web; `/docs` deshabilitado en producción.

## Vista previa pública de staging

La versión 1.4 incluye `render.yaml` para levantar una prueba HTTPS de web + API + PostgreSQL sin activar pagos ni proveedores de IA de pago. Consulta [docs/staging-render.md](docs/staging-render.md) y ejecuta el checklist de [docs/staging-test-checklist.md](docs/staging-test-checklist.md) antes de considerar un lanzamiento.

## Documentación

- [Arquitectura](docs/architecture.md)
- [Guía de desarrollo](docs/development.md)
- [Operaciones](docs/operations.md)
- [Uso en celular y PWA](docs/mobile.md)
- [ADR-001: Monorepo y stack tecnológico](docs/decisions/ADR-001-monorepo-y-stack-tecnologico.md)

## Tutor IA de texto

Por defecto el MVP usa `AI_PROVIDER=rule_based`, un proveedor local y determinista para probar el flujo sin costos externos. Para conversación generativa real se puede configurar un proveedor compatible con OpenAI mediante:

```env
AI_PROVIDER=openai_compatible
AI_BASE_URL=https://api.openai.com/v1
AI_MODEL=<modelo-del-proveedor>
AI_API_KEY=<secreto-local-no-versionado>
```

El dominio `tutor` persiste sesiones, turnos, correcciones y patrones de error. La lógica está desacoplada del proveedor para poder cambiar modelo o servicio sin rehacer el producto.

## Hoja de ruta

1. Refresh tokens y verificación de email.
2. Generación automática de `shared-types` desde OpenAPI.
3. Historial de sesiones y panel visible de memoria pedagógica. ✅
4. Traductor de texto ES/EN/SR desacoplado del proveedor. ✅
5. Práctica oral básica con STT/TTS del navegador. ✅
6. Evaluación de pronunciación y avatar. ✅
7. Suscripciones Basic/Pro y límites de uso por plan. ✅
8. Panel administrativo y preparación del modelo de pagos. ✅
9. Integración real de checkout/webhooks.
10. App móvil nativa (la PWA instalable ya está disponible).


## Licencia

Propietaria — todos los derechos reservados (ajustar según corresponda).

---

## Notas de la versión consolidada (MVP v0.1.0-async)

> **Migración a SQLAlchemy async**: `apps/api` usa `create_async_engine` + `asyncpg`
> (driver async de PostgreSQL) y `aiosqlite` para tests. Todos los endpoints son `async def`
> y el driver de alembic es convertido automáticamente de `+asyncpg` → `+psycopg` en `alembic/env.py`.

**Cambios respecto al scaffold inicial:**

| Archivo | Cambio |
|---------|--------|
| `apps/api/requirements.txt` | Añadido `asyncpg==0.30.0` |
| `apps/api/requirements-dev.txt` | `pytest-asyncio==0.25.3`, `aiosqlite==0.20.0` |
| `apps/api/app/core/database.py` | `create_async_engine` + `async_sessionmaker` |
| `apps/api/app/core/health.py` | Endpoint readiness usa `async def` y `AsyncSession` |
| `apps/api/app/domains/auth/{router,service,dependencies}.py` | Todo `async def` + `AsyncSession` |
| `apps/api/app/domains/{users,languages,lessons}/{router,service}.py` | Todo `async def` + `AsyncSession` |
| `apps/api/app/tests/conftest.py` | Fixtures async con `aiosqlite` y `pytest-asyncio` |
| `apps/api/app/tests/test_*.py` | Tests `async def` con `asyncio_mode = auto` |
| `apps/api/pyproject.toml` | `asyncio_mode = "auto"` |
| `apps/api/alembic/env.py` | Convierte `+asyncpg` → `+psycopg` para Alembic CLI |
| `docker-compose.yml` | `DATABASE_URL` usa `postgresql+asyncpg://` |
| `apps/api/.env.example` | `DATABASE_URL` usa `postgresql+asyncpg://` |

---

## Actualización local v0.2.0 — acceso web y onboarding

Esta revisión añade el flujo web que faltaba en el MVP consolidado:

- `/register`: registro conectado a `POST /api/v1/auth/register` y creación automática de sesión.
- `/login`: inicio de sesión conectado a `POST /api/v1/auth/login`.
- Sesión web mediante cookie `HttpOnly`, `SameSite=Lax` y `Secure` en producción; el JWT no se expone a JavaScript del navegador.
- `/onboarding`: persiste idioma nativo y meta diaria en `/api/v1/users/me/profile`, e idioma objetivo/nivel MCER en `/api/v1/users/me/languages`.
- `/dashboard`: requiere sesión válida, muestra perfil, idioma principal, nivel y meta diaria.
- Cierre de sesión mediante `/api/session/logout`.
- La web utiliza Route Handlers de Next.js como capa BFF para las operaciones autenticadas.

No se modificó el backend FastAPI ni se añadieron dependencias nuevas. El tutor IA, voz, pronunciación, avatar y pagos siguen fuera de esta revisión.

---

## Actualización local v0.3.0 — Tutor IA de texto

Esta revisión añade el primer módulo pedagógico funcional:

- `/tutor` en la web, protegido por sesión y adaptado al idioma/nivel principal del estudiante.
- Personalidades de tutor: amigable, paciente y profesional.
- Persistencia de sesiones y turnos en PostgreSQL mediante `tutor_sessions` y `tutor_turns`.
- Correcciones, explicaciones y traducciones opcionales por respuesta.
- `learning_memories` para registrar errores recurrentes y su frecuencia.
- Proveedor gratuito `rule_based` para desarrollo sin API externa.
- Adaptador `openai_compatible` opcional y configurable solo por variables de entorno.
- Migración Alembic `002_tutor_text_mvp.py` y pruebas específicas del dominio tutor.

La versión sigue siendo **solo texto**. STT, TTS, análisis fonético y avatar quedan fuera de v0.3.0.


---

## Actualización local v0.4.0 — historial y seguimiento de aprendizaje

Esta revisión convierte las sesiones del tutor en una experiencia consultable y reutilizable:

- `/history`: lista las conversaciones guardadas, fecha de actualización, idioma, nivel y personalidad del tutor.
- `/history/[sessionId]`: muestra la transcripción completa con correcciones, explicaciones y apoyos registrados.
- Una conversación previa puede retomarse desde `/tutor?session=<id>` sin crear una sesión nueva.
- `/progress`: resume actividad de práctica y muestra patrones de error ordenados por frecuencia.
- Nuevo endpoint `GET /api/v1/tutor/stats` con métricas descriptivas de sesiones, mensajes, correcciones y patrones recurrentes.
- El dashboard muestra accesos directos al historial y al seguimiento.
- La navegación cambia cuando existe sesión web y expone Tutor, Historial, Progreso y Panel.
- No se añadió una migración de base de datos: v0.4 reutiliza `tutor_sessions`, `tutor_turns` y `learning_memories` creadas en v0.3.

Las métricas de `/progress` describen actividad y patrones detectados; no se presentan como una certificación ni como una medición automática del nivel MCER.


---

## Actualización local v0.5.0 — traductor de texto

Esta revisión añade un traductor integrado al producto sin introducir costos obligatorios de API:

- `/translator`: interfaz autenticada para traducir entre español, inglés y serbio, con intercambio de idiomas, ejemplos y copia del resultado.
- Nuevo endpoint `POST /api/v1/translate`, protegido por JWT y validado para los tres idiomas de lanzamiento.
- Proveedor local `rule_based` con frases frecuentes de demostración y soporte de patrones como `Me llamo ...`, para probar el flujo sin consumir servicios externos.
- El mismo adaptador `openai_compatible` utilizado por el producto permite traducción de texto libre al configurar `AI_PROVIDER`, `AI_MODEL` y `AI_API_KEY`.
- La respuesta puede incluir una nota pedagógica breve sin mezclarla con el texto traducido.
- La UI y el contrato dejan separados texto, idioma origen y destino para añadir STT/TTS en la siguiente fase sin rehacer el módulo.

El proveedor local no pretende reemplazar un motor de traducción general: cuando una frase libre no está en el catálogo de demostración, devuelve un error explícito en lugar de inventar una traducción.


---

## Actualización local v0.6.0 — voz básica

La web incorpora una primera capa oral sin costos obligatorios de API:

- El Traductor permite dictar el texto de origen y escuchar el resultado.
- El Tutor permite dictar mensajes y escuchar su respuesta más reciente.
- Se utilizan `SpeechRecognition`/`webkitSpeechRecognition` cuando el navegador lo ofrece y `speechSynthesis` para TTS.
- Idiomas configurados: `es-ES`, `en-US` y `sr-RS`.
- Si el navegador no soporta una capacidad, la interfaz la deshabilita y muestra un mensaje en lugar de simular que funciona.
- No hay evaluación fonética en esta versión; esa función requiere comparar audio y fonemas con un motor especializado.

La voz sigue siendo una capa de entrada/salida: el backend recibe texto, por lo que un proveedor STT/TTS profesional podrá sustituir al motor del navegador más adelante sin rehacer Tutor o Traductor.


## Actualización local v0.7.0 — práctica de pronunciación

La ruta `/pronunciation` añade ejercicios por idioma y nivel MCER. El usuario escucha una frase, la repite con el micrófono y el backend compara la transcripción reconocida con la frase objetivo. Se guardan intentos y métricas básicas.

**Alcance de esta versión:** el puntaje es una medida de coincidencia de transcripción (palabras + similitud textual). No es todavía una medición acústica de fonemas, formantes, entonación ni posición articulatoria. Ese análisis requiere un motor de audio dedicado en una fase posterior.


## Actualización local v0.8.0 — avatar tutor ligero

- Tres perfiles visuales de tutor: Lia, Alex y Mila.
- Avatar animado sin APIs ni dependencias externas.
- Estados visuales sincronizados con dictado, procesamiento y síntesis de voz.
- Selección de avatar persistida en el navegador.
- Vista previa de voz con ritmo y tono sutilmente ajustados por perfil.
- El avatar sigue siendo una capa de presentación: no altera el motor pedagógico ni los datos del estudiante.


## Actualización local v0.9.0 — planes Basic/Pro y límites de uso

La aplicación incorpora una primera capa comercial sin activar cobros todavía:

- Plan **Basic** por defecto: 20 mensajes al Tutor IA, 30 traducciones y 10 intentos de pronunciación por día.
- Plan **Pro** preparado: 200 mensajes al Tutor IA, 500 traducciones y 100 intentos de pronunciación por día.
- Nueva ruta web `/plans` con comparación de planes, beneficios y consumo diario del usuario autenticado.
- Nuevos endpoints `GET /api/v1/billing/plans`, `GET /api/v1/billing/me` y `POST /api/v1/billing/me/request-upgrade`.
- Tablas `subscriptions` y `usage_events` mediante migración Alembic `004`.
- Los límites solo se consumen después de una operación exitosa de Tutor, Traductor o Pronunciación.
- Cuando se alcanza una cuota, la API devuelve `429 Too Many Requests` con un mensaje claro.
- El botón Pro registra interés (`requested_plan=pro`), pero **no activa el plan ni cobra al usuario**. El checkout se conectará en una fase posterior.

Los contadores diarios usan UTC en esta versión. Antes de producción conviene decidir si el reinicio comercial se hará en UTC o según la zona horaria del usuario.


---

## Actualización v1.0.0 — administración y preparación de pagos

La versión 1.0 añade un panel administrativo protegido por `is_superuser`, control manual de planes Basic/Pro, activación/desactivación de cuentas, solicitudes Pro y auditoría de cambios.

Para habilitar un administrador local después de crear la cuenta:

```bash
make promote-admin e="admin@dominio.com"
```

La estructura de `subscriptions` ahora reserva campos neutrales de proveedor (`payment_provider`, identificadores externos, periodo y cancelación al final del periodo). La configuración incluye variables para una futura integración Stripe, pero **v1.0 no procesa cobros, no crea checkouts y no recibe webhooks**. Esta separación permite probar el producto y la operación administrativa sin simular que existe una pasarela activa.

Consulta `CHANGELOG-v1.0.0.md` y `VALIDATION-v1.0.0.md` para el detalle de cambios y verificaciones.

## Cuenta y seguridad (v1.1)

La versión 1.1 incorpora perfil de cuenta, cambio/recuperación de contraseña y verificación de correo.

Para desarrollo local puede usarse:

```env
EMAIL_DELIVERY_MODE=console
EMAIL_FROM=no-reply@localhost
APP_PUBLIC_URL=http://localhost:3000
```

Los enlaces aparecerán en los logs de la API. **No usar `console` en staging/production**; la configuración lo rechaza. Para producción configure `EMAIL_DELIVERY_MODE=smtp` y los campos `SMTP_*` correspondientes.

Rutas web añadidas: `/account`, `/forgot-password`, `/reset-password`, `/verify-email`, `/privacy`, `/terms`, `/cookies`.

## Despliegue de referencia (v1.2)

La versión 1.2 incorpora un stack de producción opcional con Docker Compose + Caddy (HTTPS automático). No contiene dominios ni credenciales reales.

```bash
cp .env.production.example .env.production
# editar todos los valores change-me y apuntar DNS al servidor
make prod-preflight
make prod-build
make prod-migrate
make prod-up
make prod-smoke
```

Consulta `docs/deployment.md` y `docs/release-checklist.md` antes de publicar.


---

## Actualización v1.3.0 — uso en celular y PWA

Esta revisión adapta LinguaAI Coach para uso cotidiano desde teléfonos y tabletas:

- Manifest PWA e iconos 192/512 + Apple Touch Icon.
- Instalación desde navegadores compatibles para abrir LinguaAI desde la pantalla de inicio.
- Service worker mínimo: solo almacena el shell offline y recursos estáticos; no cachea API, JWT ni contenido privado.
- Pantalla `/offline` cuando no hay conexión.
- Navegación inferior móvil para Tutor, Traductor, Pronunciación y accesos adicionales.
- Ajustes para `safe-area` de iPhone, teclado móvil, tamaños táctiles y `100dvh`.
- Aviso de instalación para Android/Chromium y ayuda de “Añadir a pantalla de inicio” en iOS.

La PWA requiere Internet para Tutor IA, traducción, autenticación y sincronización. Las funciones de voz dependen del soporte de reconocimiento y síntesis del navegador/dispositivo.
