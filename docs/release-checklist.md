# Checklist previo a lanzamiento

## Infraestructura

- [ ] `APP_DOMAIN` y `API_DOMAIN` resuelven al servidor.
- [ ] Puertos públicos limitados a 80/443.
- [ ] `.env.production` tiene permisos restrictivos y no está versionado.
- [ ] `make prod-preflight` pasa sin errores.
- [ ] `make prod-build` finaliza correctamente.
- [ ] `make prod-migrate` finaliza correctamente.
- [ ] `make prod-up` deja todos los servicios healthy.
- [ ] `make prod-smoke` pasa.

## Cuenta y seguridad

- [ ] `SECRET_KEY` es aleatorio y >= 32 caracteres.
- [ ] `DEBUG=false`.
- [ ] CORS permite únicamente el dominio web real.
- [ ] No existen credenciales demo o contraseñas por defecto.
- [ ] Se creó el primer administrador de forma explícita.
- [ ] Flujo de cambio/recuperación de contraseña probado.
- [ ] Si se requiere verificación de email, SMTP real probado.

## Producto

- [ ] Registro, login y logout probados desde navegador.
- [ ] Onboarding y perfil persisten.
- [ ] Tutor, traductor y pronunciación probados en ES/EN/SR.
- [ ] Voz probada al menos en Chrome/Edge desktop y móvil objetivo.
- [ ] Cuotas Basic/Pro verificadas.
- [ ] Panel admin restringido a rol admin.

## Datos y operación

- [ ] Backup inicial creado y copiado fuera del servidor.
- [ ] Restauración ensayada en staging.
- [ ] Política de retención definida.
- [ ] Logs revisados para evitar exposición de secretos o PII sensible.

## Comercial / legal

- [ ] Términos, privacidad y cookies sustituyen los borradores.
- [ ] Responsable del tratamiento, contacto y jurisdicción definidos.
- [ ] Precio, moneda, impuestos y política de reembolsos definidos antes de activar pagos.
- [ ] Proveedores externos de IA/voz/correo documentados en la política de privacidad.
