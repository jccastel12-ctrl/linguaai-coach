# LinguaAI Coach v1.1.0 — Cuenta, seguridad y preparación de lanzamiento

## Añadido

- Centro de cuenta en `/account` para editar nombre, nombre visible, idioma nativo, meta diaria y biografía.
- Cambio de contraseña autenticado con invalidación de tokens anteriores mediante `auth_version`.
- Recuperación de contraseña con tokens aleatorios de un solo uso, almacenados únicamente como SHA-256.
- Verificación de correo con enlaces de un solo uso y vencimiento.
- Adaptador de correo configurable: `disabled`, `console` (solo desarrollo) o `smtp`.
- Páginas web `/forgot-password`, `/reset-password` y `/verify-email`.
- Migración `006_account_security.py` y tabla `account_tokens`.
- Campo `email_verified_at` para el usuario.
- Borradores de `/privacy`, `/terms` y `/cookies`, marcados expresamente para revisión legal antes de producción.
- Enlaces de cuenta y documentos legales en la navegación/footer.

## Seguridad

- Los tokens de recuperación/verificación no se guardan en texto plano.
- La solicitud de recuperación devuelve una respuesta indistinguible exista o no la cuenta para reducir enumeración de usuarios.
- Un cambio o restablecimiento de contraseña incrementa `auth_version`, invalidando JWT anteriores.
- `EMAIL_DELIVERY_MODE=console` está prohibido por configuración en staging/production.
- No se activa ningún proveedor real ni se incluyen credenciales.

## Pendiente antes de lanzamiento público

- Configurar y validar SMTP/transaccional real.
- Añadir rate limiting a solicitudes de recuperación y verificación.
- Ejecutar la suite completa con dependencias instaladas y PostgreSQL real.
- Revisión jurídica y adaptación de textos legales a la entidad responsable, jurisdicción y políticas comerciales definitivas.
