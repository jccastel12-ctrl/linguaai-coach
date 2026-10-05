# Validación de LinguaAI Coach v0.9.0

Fecha: 2026-10-04

## Verificado

- `python -m compileall` sobre la API y las migraciones: **correcto**.
- 41 archivos TypeScript/TSX analizados con el compilador TypeScript mediante `transpileModule`: **0 errores sintácticos**.
- `packages/shared-types`: `tsc --noEmit` **correcto**.
- JSON del monorepo y `package-lock.json`: válidos y actualizados a v0.9.0 en los paquetes propios.
- Migración `004` encadenada después de `003`.
- Se añadieron pruebas de API para catálogo de planes, plan Basic inicial, registro de uso, límite 429, capacidad Pro y solicitud de upgrade.

## No ejecutado completamente

### Pytest

La suite no pudo iniciar en este entorno porque falta la dependencia de desarrollo `aiosqlite`. El fallo ocurre al cargar `conftest.py`, antes de ejecutar tests. `aiosqlite` ya figura en `apps/api/requirements-dev.txt`; en un entorno de desarrollo normal se debe ejecutar la instalación de dependencias antes de `pytest`.

### Build/typecheck completo de Next.js

El ZIP no incluye `node_modules`. El `tsc` de la aplicación web no puede resolver `next`, `react`, `@types/node` ni el enlace de workspace `@linguaai/shared-types` hasta ejecutar `npm install`. Por ello no se presenta un build de Next.js como aprobado.

La validación sintáctica de los archivos TS/TSX sí fue realizada de forma independiente y no reportó errores.

## Pruebas recomendadas al desplegar

1. `npm install` en la raíz y `npm run typecheck --workspaces --if-present`.
2. Instalar `apps/api/requirements-dev.txt` y ejecutar `pytest -q`.
3. Ejecutar `alembic upgrade head` contra PostgreSQL real.
4. Crear usuario y confirmar plan Basic.
5. Probar Tutor, Traducción y Pronunciación hasta alcanzar sus límites.
6. Confirmar HTTP 429 al superar cuota Basic.
7. Cambiar un usuario de prueba a Pro desde administración/base de datos y confirmar cuotas ampliadas.
8. Verificar `/plans` en escritorio y móvil.
