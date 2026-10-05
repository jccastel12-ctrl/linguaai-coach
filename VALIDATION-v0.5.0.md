# Validación — LinguaAI Coach v0.5.0

## Verificaciones ejecutadas

- `python3 -m compileall -q apps/api/app` → **OK**.
- Prueba directa del proveedor local de traducción → **OK** para:
  - `Necesito ayuda` (ES→EN) → `I need help`.
  - `Thank you` (EN→SR) → `Hvala`.
  - `Me llamo Ana` (ES→SR) → `Zovem se Ana`.
  - `Здраво` (SR cirílico→ES) → `Hola`.
- Validación Pydantic → **OK**: rechaza idioma origen y destino iguales.
- Proveedor local → **OK**: rechaza explícitamente texto libre no reconocido en lugar de inventar una traducción.
- Parseo sintáctico de TypeScript/TSX con el compilador TypeScript global → **31 archivos, 0 errores de sintaxis**.
- JSON válido en `package.json`, `package-lock.json`, `apps/web/package.json` y `packages/shared-types/package.json` → **OK**.

## Verificaciones no completadas

### Pytest completo
No pudo ejecutarse porque el entorno actual no tiene instalado `aiosqlite`, dependencia de las fixtures de prueba. El fallo ocurre al cargar `conftest.py`, antes de ejecutar los tests de traducción.

### Typecheck/build completo de Next.js
El ZIP no incluye `node_modules`. `npm run typecheck` no puede resolver `next`, `react`, `@types/node` ni el workspace enlazado hasta ejecutar `npm install`/`npm ci`. Por esa razón no se marca el typecheck ni el build como aprobados.

## Alcance funcional de v0.5

- Traductor de texto autenticado ES/EN/SR.
- Modo local gratuito para un catálogo controlado de frases de demostración.
- Traducción de texto libre preparada mediante proveedor `openai_compatible` configurable por variables de entorno.
- Sin nuevas tablas ni migraciones de base de datos.
- Preparado para añadir STT/TTS en la siguiente fase.
