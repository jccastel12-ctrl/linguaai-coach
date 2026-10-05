# LinguaAI Coach v0.7.0 — Pronunciation Practice MVP

## Añadido

- Dominio backend `pronunciation` con ejercicios para español, inglés y serbio en niveles A1–C2.
- Endpoint autenticado `GET /api/v1/pronunciation/exercises`.
- Endpoint autenticado `POST /api/v1/pronunciation/evaluate`.
- Endpoint `GET /api/v1/pronunciation/stats` y listado de intentos recientes.
- Persistencia de intentos en `pronunciation_attempts` mediante migración Alembic `003`.
- Página web `/pronunciation` con escucha de referencia, captura por micrófono, evaluación y feedback.
- Puntuación de 0–100 basada en similitud de transcripción y coincidencia de palabras.
- Normalización especial para comparar serbio en alfabeto latino y cirílico.
- Estadísticas de pronunciación incorporadas a `/progress`.
- Acceso directo desde el dashboard y navegación principal.

## Límite deliberado del MVP

La v0.7 no afirma medir fonemas ni calidad acústica real. Usa el texto reconocido por el navegador como aproximación útil y gratuita para validar el flujo pedagógico. El análisis fonético real se deja para una futura capa STT/audio con alineación forzada o un proveedor especializado.
