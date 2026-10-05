# Validación v1.2.0 — preparación de despliegue

## Verificaciones realizadas

- `python3 -m compileall -q apps/api/app`: **OK**.
- Sintaxis POSIX shell (`sh -n`) en `scripts/*.sh` e `infra/docker/*.sh`: **OK**.
- Parseo de todos los archivos JSON del repositorio: **OK**.
- `tsc -p packages/shared-types/tsconfig.json --noEmit`: **OK**.
- Parseo YAML de `compose.production.yml` y `docker-compose.yml` con PyYAML: **OK**.
- Preflight con placeholders: **rechazado correctamente**.
- Preflight con configuración de prueba válida: **OK**.
- Integridad del ZIP final: se verifica después de empaquetar.

## Verificaciones no ejecutadas

- `docker compose config`: Docker Compose CLI no está disponible en este entorno.
- Arranque real de Caddy/TLS: requiere Docker, DNS públicos y puertos 80/443 accesibles.
- PostgreSQL real: no se levantó un servidor PostgreSQL en este entorno.
- Suite completa `pytest`: no inicia porque falta la dependencia de desarrollo `aiosqlite` en el entorno actual (`ModuleNotFoundError`). No se modificó el entorno global para instalar dependencias.
- `next build`: `node_modules` no está incluido en el ZIP y no se instalaron dependencias de red.
- Smoke test público: requiere dominio/despliegue reales.

## Qué valida esta entrega

La v1.2 agrega artefactos de despliegue y operación sin afirmar que exista un servidor público ya desplegado. Antes de publicar, ejecutar en un host con Docker:

1. `make prod-preflight`
2. `make prod-build`
3. `make prod-migrate`
4. `make prod-up`
5. `make prod-smoke`

Además, completar `docs/release-checklist.md`.
