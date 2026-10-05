# LinguaAI Coach v1.3.0 — Móvil y PWA

## Añadido

- `apps/web/public/manifest.webmanifest` con modo `standalone`.
- Iconos PWA 192×192, 512×512 y Apple Touch Icon 180×180.
- `apps/web/public/sw.js` con caché conservadora de shell/recursos estáticos y fallback `/offline`.
- `PwaClient`: registro del service worker, instalación en navegadores compatibles y ayuda específica para iOS.
- `MobileNav`: navegación inferior para usuarios autenticados y hoja “Más” con Historial, Progreso, Planes, Cuenta y Administración.
- Página `/offline`.
- Metadata web-app, `viewport-fit=cover`, `themeColor` y Apple Web App.
- Ajustes responsive para safe areas, teclado móvil, alturas dinámicas y objetivos táctiles.
- `docs/mobile.md`.

## Seguridad y privacidad

- El service worker no intercepta `/api/*`.
- No se cachean respuestas autenticadas ni JWT.
- El contenido privado no se convierte en contenido offline en esta fase.

## Alcance

La v1.3 ofrece una PWA instalable; no es todavía un binario nativo de Android/iOS. Tutor, traductor y sincronización siguen requiriendo Internet. La voz depende de las capacidades del navegador y dispositivo.
