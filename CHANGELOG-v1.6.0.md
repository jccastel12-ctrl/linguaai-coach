# LinguaAI Coach v1.6.0 — AI reliability

## Cambios

- Añade reintentos automáticos para errores transitorios del proveedor de IA (`408`, `425`, `429`, `500`, `502`, `503`, `504`) y fallos de red/timeout.
- Añade backoff exponencial configurable para evitar fallar de inmediato durante saturaciones breves.
- Añade `AI_FALLBACK_MODEL` opcional. Si el modelo principal sigue fallando o no existe, LinguaAI prueba un segundo modelo antes de responder con error.
- Centraliza el cliente OpenAI-compatible en `app/core/ai_client.py` para que la misma protección cubra Traductor y Tutor IA.
- Evita enviar `temperature` a Gemini 3.x, donde Google lo marca como parámetro obsoleto.
- Mejora los mensajes de error sin exponer claves, prompts ni respuestas privadas en los logs.
- No modifica base de datos ni requiere migración Alembic.

## Configuración recomendada para el staging actual con Gemini

```text
AI_MODEL=gemini-3.5-flash-lite
AI_FALLBACK_MODEL=gemini-3.6-flash
AI_RETRY_ATTEMPTS=3
AI_RETRY_BACKOFF_SECONDS=0.7
```

El tutor puede seguir en `AI_PROVIDER=rule_based` hasta que se decida activarlo con Gemini.
