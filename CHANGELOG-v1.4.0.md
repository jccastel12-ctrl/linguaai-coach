# LinguaAI Coach v1.4.0 - Staging público y prueba móvil

## Añadido
- `render.yaml` para desplegar un entorno de prueba público con web, API y PostgreSQL.
- Normalización automática de URLs PostgreSQL administradas (`postgresql://` / `postgres://`) a `postgresql+asyncpg://`.
- Pruebas unitarias para esa normalización.
- `scripts/smoke-staging.sh` para comprobar web, liveness y readiness.
- `docs/staging-render.md` con el flujo de despliegue y prueba en Android/iPhone.
- `docs/staging-test-checklist.md` con pruebas funcionales antes del lanzamiento.
- El comando `start` de Next.js acepta ahora el puerto asignado por la plataforma de hosting.

## Sin cambios intencionales
- No se habilitaron pagos.
- No se añadió ningún proveedor de IA de pago.
- No se añadieron secretos.
- No se modificó el modelo de datos.
