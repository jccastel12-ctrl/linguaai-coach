# Validación — LinguaAI Coach v1.0.0

Fecha: 2026-10-04

## Verificaciones ejecutadas

- `python -m compileall` sobre `apps/api/app` y migraciones Alembic: **OK**.
- Parseo JSON de `package.json`, `apps/web/package.json`, `packages/shared-types/package.json` y `package-lock.json`: **OK**.
- Parseo/transpilación sintáctica con TypeScript de todos los archivos `.ts/.tsx` de web y tipos compartidos: **0 errores de sintaxis**.
- `tsc --noEmit -p packages/shared-types/tsconfig.json`: **OK**.

## Suite Pytest

Se intentó ejecutar:

```bash
cd apps/api && python -m pytest app/tests -q
```

No pudo iniciar porque el entorno de ejecución actual no contiene `aiosqlite`, dependencia de tests declarada en `requirements-dev.txt`.

También se intentó instalar `aiosqlite==0.20.0`, pero el entorno no tiene resolución/acceso de red hacia el índice de paquetes. Por ello **no se reporta la suite completa como aprobada**.

## Integración de base de datos

- No se ejecutó Docker Compose ni PostgreSQL real en este entorno.
- La migración `005_admin_payment_readiness.py` usa `batch_alter_table` para conservar compatibilidad con la prueba de migraciones sobre SQLite y con PostgreSQL.

## Pagos

- Checkout real: **no implementado**.
- Webhooks reales: **no implementados**.
- Cobros: **no se realizan**.
- El modelo de datos, variables de entorno y campos de proveedor quedan preparados para una integración posterior.

## Recomendación antes de producción

1. Instalar `requirements-dev.txt` y ejecutar `pytest` completo.
2. Ejecutar `alembic upgrade head` contra PostgreSQL 16 real.
3. Crear una cuenta normal y promoverla con `make promote-admin e="correo@dominio.com"`.
4. Validar `/admin` y los cambios Basic/Pro en navegador real.
5. Ejecutar `npm install`, `npm run typecheck`, `npm run build:web` y `npm run lint`.
