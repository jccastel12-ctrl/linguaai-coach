# LinguaAI Coach v0.4.0 — Historial y seguimiento

## Añadido

- Historial de sesiones en `/history`.
- Vista de conversación guardada en `/history/[sessionId]`.
- Reanudación de conversaciones existentes desde `/tutor?session=<id>`.
- Panel de seguimiento en `/progress`.
- Endpoint `GET /api/v1/tutor/stats`.
- Estadísticas de sesiones, intervenciones, correcciones y patrones recurrentes.
- Listado de memorias pedagógicas ordenadas por frecuencia.
- Navegación autenticada con accesos a Tutor, Historial, Progreso y Panel.
- Nuevos contratos TypeScript `TutorSessionDetail` y `TutorStats`.
- Prueba de API para el resumen estadístico del tutor.

## Modificado

- `TutorChat` puede iniciar con una sesión y mensajes ya existentes.
- El dashboard muestra actividad del tutor y patrones recurrentes.
- Versiones del monorepo, web, contratos compartidos y API elevadas a `0.4.0`.

## Base de datos

No hay migración nueva. Esta versión reutiliza las tablas creadas en `002_tutor_text_mvp.py`.

## Pendiente

- Ejecutar la suite completa de `pytest` en un entorno con dependencias de desarrollo instaladas.
- Ejecutar `npm run typecheck` y `npm run build` con dependencias Node instaladas.
- Probar el flujo completo contra PostgreSQL real.
- Voz, análisis de pronunciación y avatar siguen fuera de esta versión.
