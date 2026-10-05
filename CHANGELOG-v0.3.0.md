# LinguaAI Coach v0.3.0 — Tutor IA de texto MVP

## Implementado

- Nuevo dominio backend `tutor` con sesiones persistentes, turnos y memoria pedagógica.
- Endpoints autenticados para crear/listar sesiones, conversar y consultar errores frecuentes.
- Corrección de texto y explicación pedagógica almacenadas por turno.
- Memoria de errores por usuario, idioma, categoría y patrón con contador de recurrencia.
- Proveedor `rule_based` gratuito para desarrollo y demostración sin consumir APIs externas.
- Adaptador `openai_compatible` opcional mediante variables de entorno, sin credenciales incrustadas.
- Migración Alembic `002_tutor_text_mvp.py`.
- Pantalla web `/tutor` conectada al backend mediante el BFF de Next.js.
- Selector de personalidad: amigable, paciente o profesional.
- Dashboard actualizado con acceso directo al tutor.
- Contratos TypeScript compartidos para tutor, turnos y memoria.

## Límites de esta versión

- La evaluación de pronunciación, STT/TTS y avatar animado no están implementados.
- El proveedor por defecto es determinista y cubre solo reglas de demostración; para conversación generativa real debe configurarse `AI_PROVIDER=openai_compatible`, `AI_BASE_URL`, `AI_MODEL` y `AI_API_KEY`.
- La UI actual inicia conversaciones nuevas y muestra la sesión activa, pero aún no incluye historial navegable de sesiones.
