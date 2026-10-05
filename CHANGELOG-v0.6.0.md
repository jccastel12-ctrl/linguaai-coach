# LinguaAI Coach v0.6.0 — Voz básica en navegador

## Alcance

Esta versión añade práctica oral sin introducir un proveedor externo obligatorio ni modificar la base de datos.

### Traductor

- Botón **Dictar** para capturar voz en español, inglés o serbio mediante la API de reconocimiento de voz disponible en el navegador.
- Transcripción provisional visible directamente en el campo de texto.
- Botón **Escuchar** para reproducir la traducción con `speechSynthesis` y la voz instalada en el dispositivo.
- Manejo de permisos denegados, ausencia de micrófono, falta de voz y navegadores sin soporte.
- Los idiomas se mapean a `es-ES`, `en-US` y `sr-RS`.

### Tutor

- Entrada por micrófono en el compositor del Tutor IA.
- Lectura en voz alta de la respuesta más reciente del tutor.
- El texto sigue siendo la fuente de verdad de la conversación: la voz se transcribe antes de enviarse al backend.
- Las sesiones, correcciones y memoria pedagógica continúan usando los mismos endpoints y modelos de v0.3/v0.4.

### Arquitectura

- Nuevo hook compartido `apps/web/src/lib/use-browser-speech.ts`.
- No se añadieron paquetes npm ni servicios de pago.
- No se añadió migración Alembic.
- La implementación es deliberadamente desacoplada: en una fase posterior se puede reemplazar el reconocimiento/síntesis del navegador por STT/TTS de servidor sin modificar los contratos del tutor o del traductor.

## Limitaciones conocidas

- `SpeechRecognition` no tiene soporte uniforme en todos los navegadores y puede depender de servicios del proveedor del navegador.
- La disponibilidad y calidad de voces serbias dependen de las voces instaladas en el sistema operativo/navegador.
- Esta versión **no evalúa pronunciación** ni asigna puntuaciones fonéticas.
- No es conversación full-duplex ni streaming WebRTC; funciona por turnos.
