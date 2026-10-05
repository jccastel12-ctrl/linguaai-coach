# Validación v1.3.0 — móvil y PWA

## Verificaciones realizadas

- `python3 -m compileall -q apps/api/app`: **OK**.
- Transpilación sintáctica de `apps/web/src/**/*.{ts,tsx}` con TypeScript: **65 archivos, 0 errores de sintaxis**.
- `tsc -p packages/shared-types/tsconfig.json --noEmit`: **OK**.
- Parseo de archivos JSON del repositorio: **OK**.
- `node --check apps/web/public/sw.js`: **OK**.
- Iconos PWA 180/192/512: **PNG válidos**.
- Manifest PWA: **JSON válido**.

## Comportamientos revisados por diseño

- El service worker ignora `/api/*` y no cachea respuestas privadas.
- Navegaciones usan red primero y solo muestran `/offline` cuando no hay red.
- Recursos `/_next/static/*` e iconos usan caché estática.
- La navegación inferior solo se renderiza para usuarios autenticados.
- La interfaz contempla `safe-area-inset-*` y `100dvh` para pantallas móviles.
- Inputs/textarea/select usan 16 px en móvil para evitar zoom involuntario de iOS.

## Verificaciones no ejecutadas

- `next build`: no se instalaron `node_modules` en este entorno.
- Lighthouse/PWA installability real: requiere ejecutar la web mediante HTTPS en un navegador.
- Instalación real en Android/iOS: requiere URL pública/HTTPS y dispositivo físico o emulador.
- Micrófono/STT/TTS móvil: depende del navegador y sistema operativo; debe probarse en dispositivos reales.
- Suite completa `pytest`: el entorno conserva la limitación previa por dependencias de desarrollo no instaladas.

## Criterio de salida

La v1.3 queda preparada como PWA móvil instalable. Antes de lanzamiento público se debe desplegar v1.3 sobre HTTPS y realizar una matriz mínima de pruebas en Android/Chrome y iPhone/Safari, en especial para micrófono y síntesis de voz.
