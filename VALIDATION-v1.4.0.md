# Validación v1.4.0

Fecha de preparación: 2026-10-04.

## Verificado en este entorno

- `python3 -m compileall -q apps/api`: correcto.
- Importación directa de `Settings` y normalización `postgresql://` -> `postgresql+asyncpg://`: correcta.
- JSON válido en `package.json`, `package-lock.json`, `apps/web/package.json` y `packages/shared-types/package.json`.
- `render.yaml`: YAML válido; contiene 2 servicios web y 1 PostgreSQL.
- Sintaxis shell correcta en scripts de staging/producción mediante `bash -n`.
- Sintaxis del service worker correcta mediante `node --check`.
- Integridad estructural de los archivos nuevos de staging revisada.

## No ejecutado completamente

- `pytest`: no inicia en este entorno porque falta `aiosqlite`, dependencia de pruebas. El intento falla durante la carga de `conftest.py`; no se reportan pruebas como aprobadas cuando no corrieron.
- `next build` / `tsc`: no ejecutados porque el ZIP fuente no incluye `node_modules` y no se instalaron dependencias externas en esta sesión.
- Despliegue real en Render: requiere repositorio Git y una cuenta del usuario en Render.
- Pruebas reales de PWA, micrófono y TTS en Android/iPhone: requieren una URL HTTPS desplegada y dispositivo físico.

## Riesgos conocidos de staging

- El entorno gratuito de Render es apropiado para demostración, no para producción.
- La primera carga después de inactividad puede tardar por reactivación del servicio.
- La base gratuita de staging debe considerarse temporal.
- Correo, pagos e IA generativa permanecen deshabilitados por diseño.
