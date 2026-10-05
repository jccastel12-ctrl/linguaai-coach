# Validación de LinguaAI Coach v0.8.0

## Alcance validado

La versión 0.8.0 incorpora un avatar tutor ligero en el frontend. No modifica el esquema de base de datos ni añade proveedores externos.

## Comprobaciones ejecutadas

- `python -m compileall -q apps/api/app`: **correcto**.
- Lectura JSON de `package.json`, `package-lock.json`, `apps/web/package.json` y `packages/shared-types/package.json`: **correcto**.
- Transpilación sintáctica con TypeScript de todos los archivos `src/**/*.ts` y `src/**/*.tsx`: **36 archivos, 0 errores sintácticos**.
- Versiones de root, web, shared-types y API actualizadas a `0.8.0`.

## Aspectos no verificados en este entorno

- `next build` y el `typecheck` completo de la aplicación web no se ejecutaron porque el ZIP de trabajo no incluye `node_modules` y este entorno no dispone de las dependencias locales de Next/React.
- No se realizó una prueba visual en navegador real. Las animaciones deben comprobarse en Chrome/Edge/Safari junto con micrófono y síntesis de voz.
- La voz sigue usando `SpeechSynthesis` del dispositivo. El nombre del avatar no implica que exista una voz humana específica instalada; se aplican únicamente ajustes suaves de ritmo y tono.

## Criterios funcionales implementados

- Tres perfiles visuales: Lia, Alex y Mila.
- Persistencia local de la selección de avatar.
- Estado `listening` al dictar.
- Estado `thinking` mientras el backend procesa el turno.
- Estado `speaking` durante TTS.
- Estado `idle` en reposo.
- Botón de vista previa de voz.
- Accesibilidad con `prefers-reduced-motion`.
- Sin API adicional, sin costes de avatar y sin migración de base de datos.
