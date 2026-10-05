# Checklist de prueba v1.4

## Acceso y cuenta
- [ ] La web abre por HTTPS.
- [ ] Registro crea una cuenta.
- [ ] Login redirige al dashboard.
- [ ] Logout elimina la sesión.
- [ ] Onboarding guarda idioma y nivel.

## Aprendizaje
- [ ] Tutor crea una sesión y responde.
- [ ] Historial muestra sesiones anteriores.
- [ ] Progreso muestra métricas.
- [ ] Traductor ES/EN/SR responde.
- [ ] Pronunciación guarda intentos.

## Celular / PWA
- [ ] Diseño usable a 360 px de ancho.
- [ ] Micrófono solicita permiso por HTTPS.
- [ ] TTS reproduce una respuesta.
- [ ] La PWA se instala en pantalla de inicio.
- [ ] La navegación inferior no queda tapada por la zona segura del teléfono.

## Administración
- [ ] Una cuenta normal no abre `/admin`.
- [ ] Un administrador sí abre `/admin`.
- [ ] Los límites Basic se aplican.
- [ ] La solicitud de Pro no activa cobro real.

## Infraestructura
- [ ] `/health` devuelve 2xx.
- [ ] `/health/ready` devuelve 2xx.
- [ ] Alembic llegó a `head`.
- [ ] No hay secretos en Git.
