# Validación v1.1.0

## Verificado en este entorno

- `python -m compileall -q apps/api/app apps/api/alembic`: **OK**.
- JSON de `package.json` raíz y `apps/web/package.json`: **OK**.
- `@linguaai/shared-types` fue actualizado con `email_verified_at`; el typecheck aislado no produjo salida de error.
- El ZIP final se valida posteriormente con `unzip -t`.

## No verificado de extremo a extremo

- `pytest`: no pudo arrancar porque el entorno no tiene instalado `aiosqlite`, dependencia ya declarada para desarrollo/pruebas. Error observado: `ModuleNotFoundError: No module named 'aiosqlite'`.
- `next build` / typecheck completo de la web: no hay `node_modules`; TypeScript no puede resolver `next`, `react`, `@types/node` ni el workspace compartido. Los errores observados corresponden a dependencias ausentes, por lo que no se declara el build como aprobado.
- SMTP real: no se configuraron credenciales ni servidor de correo.
- PostgreSQL real y migración 006: no hay servidor PostgreSQL disponible en este entorno.

## Pruebas nuevas escritas

`apps/api/app/tests/test_account_security.py` cubre:

- respuesta anti-enumeración en solicitud de reset;
- restablecimiento de contraseña;
- invalidación del JWT anterior mediante `auth_version`;
- verificación de correo con token de un solo uso;
- rechazo del cambio de contraseña con contraseña actual incorrecta.

Estas pruebas quedan listas para ejecutarse en CI/local una vez instaladas las dependencias.
