# Uso en celular y PWA

LinguaAI Coach v1.3 puede utilizarse desde un navegador móvil y puede instalarse como una Progressive Web App (PWA) sin publicar todavía una app nativa en App Store o Google Play.

## Qué significa para el usuario

- Abrir la URL pública desde el teléfono.
- Iniciar sesión con la misma cuenta que en escritorio.
- Usar Tutor, Traductor, Pronunciación, Historial, Progreso y Cuenta.
- Instalar un acceso de LinguaAI en la pantalla de inicio cuando el navegador lo permita.
- Abrir la PWA en modo independiente, sin la barra normal del navegador.

## Android / navegadores Chromium

Cuando el navegador emita el evento de instalación, LinguaAI muestra un aviso **Instalar**. También puede aparecer la opción "Instalar aplicación" o "Añadir a pantalla de inicio" en el menú del navegador.

## iPhone / iPad

La interfaz muestra una indicación para usar Safari → **Compartir** → **Añadir a pantalla de inicio**. La disponibilidad exacta de reconocimiento de voz y voces sintetizadas depende de la versión de iOS y del navegador.

## Sin conexión

El service worker de v1.3 es deliberadamente conservador:

- cachea iconos, manifest y la pantalla `/offline`;
- puede cachear recursos estáticos de Next.js;
- no cachea llamadas `/api/*`;
- no guarda contenido privado del usuario para uso offline;
- no pretende ofrecer Tutor o Traductor sin Internet.

Si falla la red durante una navegación, la PWA muestra una página que explica que las funciones inteligentes necesitan conexión.

## Voz

La v1.3 conserva la capa de voz del navegador. El micrófono requiere HTTPS en producción y permiso explícito del usuario. El reconocimiento y la síntesis pueden variar por dispositivo, idioma y navegador. Para calidad uniforme en una versión comercial futura, sustituir esta capa por STT/TTS del backend.

## App nativa

La PWA cubre el MVP móvil sin mantener dos codebases. Una app nativa con Flutter o React Native puede añadirse más adelante si hacen falta notificaciones push avanzadas, audio de baja latencia, procesamiento fonético nativo, publicación en tiendas o integración profunda con el sistema operativo.
