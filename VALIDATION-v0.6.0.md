# Validación v0.6.0

## Verificaciones realizadas

- `python -m compileall apps/api/app`: sintaxis Python válida.
- JSON de `package.json`, `apps/web/package.json`, `packages/shared-types/package.json` y `package-lock.json`: parseo correcto.
- Revisión estática de los componentes modificados: `TranslatorPanel.tsx`, `TutorChat.tsx` y `use-browser-speech.ts`.
- La integración de voz no cambia contratos HTTP ni esquema de base de datos.

## Verificaciones no ejecutadas

- `next build` y el `typecheck` completo del workspace no se consideran validados porque el ZIP no incluye `node_modules` y este entorno no dispone de una instalación local de las dependencias React/Next del proyecto.
- Las pruebas reales de micrófono y altavoz requieren un navegador con permisos de audio y no pueden comprobarse desde este entorno de línea de comandos.
- La calidad de STT/TTS en serbio debe verificarse en los navegadores objetivo; depende del motor y voces disponibles en cada dispositivo.

## Criterio para producción

Antes de publicar, ejecutar en un navegador HTTPS real:

1. Permitir micrófono.
2. Probar dictado ES, EN y SR.
3. Confirmar que el texto reconocido se puede editar antes de enviar.
4. Probar reproducción de traducción y respuesta del tutor en los tres idiomas.
5. Verificar comportamiento cuando se deniega el permiso del micrófono.
6. Ejecutar `npm ci`, `npm run typecheck`, `npm run build:web` y la suite de API.
