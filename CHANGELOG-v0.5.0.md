# LinguaAI Coach — v0.5.0

## Traductor integrado ES / EN / SR

### API
- Nuevo dominio `apps/api/app/domains/translation`.
- Nuevo endpoint autenticado `POST /api/v1/translate`.
- Validación de idioma origen/destino y texto de hasta 5000 caracteres.
- Proveedor `rule_based` gratuito para demostración con frases frecuentes y un patrón dinámico de presentación personal.
- Soporte de entradas serbias básicas en cirílico dentro del modo demo.
- Proveedor `openai_compatible` para traducción libre cuando se configuran las variables de IA existentes.
- El modo local falla de forma explícita ante frases desconocidas; no simula ni inventa una traducción.

### Web
- Nueva página `/translator`.
- Selector ES / EN / SR con intercambio de idiomas.
- Ejemplos de prueba según idioma origen.
- Copia del resultado al portapapeles.
- Nota pedagógica separada de la traducción.
- Acceso desde navegación y dashboard.
- Route Handler `/api/session/translate` para mantener el JWT en cookie HttpOnly.

### Contratos
- `TranslationRequest` y `TranslationResponse` añadidos a `@linguaai/shared-types`.
- Versiones del monorepo actualizadas a 0.5.0.

### Sin cambios de base de datos
Esta versión no agrega tablas ni migraciones: la traducción de v0.5 es stateless.
