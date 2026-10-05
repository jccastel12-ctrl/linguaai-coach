# LinguaAI Coach v0.8.0 — Avatar Tutor Ligero

## Añadido

- Componente `TutorAvatar` sin dependencias externas ni servicios de pago.
- Tres perfiles visuales seleccionables: **Lia**, **Alex** y **Mila**.
- Estados visuales del avatar: `idle`, `listening`, `thinking` y `speaking`.
- Animaciones de escucha, parpadeo, pensamiento, boca y barras de voz.
- Selector de avatar persistido en `localStorage` con la clave `linguaai:tutor-avatar`.
- Presencia compacta del tutor en la cabecera de la conversación.
- Vista previa de voz para cada perfil.
- Ajustes opcionales de ritmo y tono al usar la síntesis de voz del navegador.
- Respeto de `prefers-reduced-motion` para accesibilidad.

## Cambiado

- La pantalla `/tutor` identifica al tutor elegido por nombre en las respuestas.
- El estado del avatar se sincroniza con el micrófono, la espera del backend y la reproducción TTS.
- `useBrowserSpeech.speak()` acepta ahora opciones opcionales `rate` y `pitch`, manteniendo compatibilidad con las llamadas existentes.
- Versiones del monorepo actualizadas a `0.8.0`.

## Alcance deliberado

Este avatar es una capa visual ligera para validar experiencia de producto. No es un avatar 3D ni fotorrealista, no usa lip-sync fonético y no requiere APIs externas. La arquitectura permite sustituirlo después por una solución 2D/3D o streaming sin cambiar el backend del tutor.
