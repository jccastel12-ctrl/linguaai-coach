# Vista previa pública en Render (staging)

Esta configuración está pensada para **probar LinguaAI Coach desde un computador y un celular con HTTPS real** antes de contratar infraestructura de producción.

## Qué crea `render.yaml`

- `linguaai-coach-web`: Next.js.
- `linguaai-coach-api`: FastAPI.
- `linguaai-coach-db`: PostgreSQL.
- HTTPS y subdominios `onrender.com` administrados por Render.
- Migraciones Alembic antes de desplegar la API.
- `AI_PROVIDER=rule_based`, pagos deshabilitados y correo deshabilitado, para que la prueba no consuma APIs externas.

## Antes de empezar

1. Subir el contenido de este proyecto a un repositorio Git.
2. Crear una cuenta en Render.
3. No subir `.env`, `.env.production` ni secretos al repositorio.

## Despliegue

1. En Render, crear un **Blueprint** nuevo.
2. Conectar el repositorio de LinguaAI Coach.
3. Seleccionar `render.yaml` en la raíz.
4. Revisar que se creen los dos servicios web y la base PostgreSQL.
5. Aplicar el Blueprint y esperar a que terminen las compilaciones.
6. Abrir primero la URL de `linguaai-coach-api` y comprobar `/health/ready`.
7. Abrir la URL de `linguaai-coach-web` y crear una cuenta de prueba.

El backend acepta la cadena `postgresql://` entregada por servicios administrados y la normaliza internamente a `postgresql+asyncpg://` para SQLAlchemy async.

## Prueba desde el celular

Con la URL HTTPS de `linguaai-coach-web`:

1. Abrirla en Chrome (Android) o Safari (iPhone).
2. Registrarse e iniciar sesión.
3. Probar Tutor, Traductor, Pronunciación y micrófono.
4. Instalar la PWA desde el navegador:
   - Android: menú del navegador → **Instalar app** / **Añadir a pantalla de inicio**.
   - iPhone: Safari → **Compartir** → **Añadir a pantalla de inicio**.
5. Cerrar y volver a abrir desde el icono para comprobar la experiencia instalada.

## Smoke test desde terminal

```bash
./scripts/smoke-staging.sh \
  https://<web>.onrender.com \
  https://<api>.onrender.com
```

En servicios gratuitos, la primera petición después de un periodo de inactividad puede tardar mientras el servicio vuelve a arrancar. El script deja hasta 90 segundos por petición para esta prueba.

## Limitaciones del staging gratuito

Este entorno es de demostración, no de venta pública:

- Los servicios gratuitos pueden suspenderse cuando quedan inactivos y tardar al volver a iniciar.
- La base gratuita de Render es temporal y no debe considerarse almacenamiento de producción.
- No hay pagos reales.
- El tutor sigue en modo `rule_based` salvo que se configure un proveedor de IA.
- El correo está deshabilitado. La verificación y recuperación por email requieren un proveedor compatible con producción.
- La calidad de STT/TTS depende del navegador y del dispositivo.

## Paso posterior

Una vez validado el flujo completo en teléfono y escritorio, el siguiente paso es elegir infraestructura permanente, proveedor de IA, servicio de correo y pasarela de pagos. No conviene activar ninguno antes de comprobar el producto en staging.
