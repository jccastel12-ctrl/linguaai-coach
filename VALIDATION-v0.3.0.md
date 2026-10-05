# Validación local v0.3.0

Fecha: 2026-10-04

## Comprobaciones ejecutadas

- `python -m compileall -q apps/api/app apps/api/alembic`: **OK**.
- Prueba directa del proveedor `rule_based` para inglés, español y serbio: **OK**.
  - Inglés: detecta `I have 20 years old` y propone `I am 20 years old.`
  - Inglés: detecta `I am agree` y propone `I agree`.
  - Español: detecta `yo sabo` y propone `yo sé`.
  - Serbio: detecta `ja sam 30 godina` y propone `Imam 30 godina`.
- Parseo de `package.json`, `package-lock.json`, `apps/web/package.json` y `packages/shared-types/package.json`: **OK**.
- Comprobación de sintaxis TypeScript/TSX con TypeScript 5.8.3 (`transpileModule`) sobre 24 archivos: **0 errores de sintaxis**.

## Comprobaciones no ejecutadas completamente

### Pytest de integración

No se pudo ejecutar la suite completa en este entorno porque faltan los drivers Python `aiosqlite` y `asyncpg`. El intento de instalar `aiosqlite` falló por ausencia de acceso de red del contenedor. Los tests nuevos quedan incluidos en `apps/api/app/tests/test_tutor.py` para ejecutarse en el entorno normal del proyecto o CI.

### Typecheck/build completo de Next.js

El `node_modules` heredado del ZIP estaba incompleto y faltaban archivos reales de `@types/node`, `@types/react`, `@types/react-dom` y TypeScript local. Se intentó `npm ci`, pero el entorno agotó el tiempo de transporte antes de completar la instalación. Por ello no se marca `npm run typecheck` ni `next build` como verificados. La sintaxis TS/TSX sí fue validada con el compilador TypeScript global.

## Qué debe comprobar CI o la máquina de desarrollo

```bash
make install
make test
cd apps/api && .venv/bin/alembic upgrade head
npm run typecheck
npm run build:web
```

Con PostgreSQL disponible, también debe comprobarse el flujo: registro → onboarding → crear sesión tutor → enviar mensaje → persistencia de turnos → memoria de error.
