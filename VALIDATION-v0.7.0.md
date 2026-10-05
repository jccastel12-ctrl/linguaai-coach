# Validación de LinguaAI Coach v0.7.0

## Verificado en este entorno

- `python -m compileall -q apps/api/app apps/api/alembic`: **OK**.
- Motor puro de puntuación (`score_transcript`): **OK** con coincidencia exacta en inglés, equivalencia serbio latino/cirílico y caso parcial.
- Sintaxis TypeScript/TSX mediante `typescript.transpileModule`: **OK, 36 archivos**.
- Contratos compartidos TypeScript: `tsc --noEmit -p packages/shared-types/tsconfig.json`: **OK**.
- Versiones del monorepo actualizadas a `0.7.0`.

## No ejecutado de forma completa

### Pytest / migraciones

La suite API no pudo arrancar en este entorno porque faltan `aiosqlite` y `asyncpg`. Se intentó instalar ambas dependencias, pero el entorno no tiene resolución de red. Por ello no se declara como ejecutada la prueba HTTP ni la migración 003 contra una base real.

### Typecheck/build completo de Next.js

`npm run typecheck` no puede resolver `next`, `react`, tipos de Node ni el workspace `@linguaai/shared-types` porque el ZIP de trabajo no incluye `node_modules` y no hay acceso de red para ejecutar `npm ci`. La sintaxis de los 36 archivos TS/TSX sí fue comprobada con el compilador TypeScript disponible globalmente.

## Validación recomendada en una máquina con dependencias

```bash
npm ci
npm run typecheck
npm run build:web

cd apps/api
python -m pip install -r requirements.txt -r requirements-dev.txt
pytest
alembic upgrade head
```

Luego probar en Chrome/Edge:

1. iniciar sesión;
2. abrir `/pronunciation`;
3. escuchar la frase modelo;
4. permitir el micrófono;
5. repetir la frase;
6. evaluar y confirmar que se guarda el intento;
7. revisar `/progress` para ver el promedio.

## Interpretación correcta del puntaje

La v0.7 mide **coincidencia de transcripción**: compara la frase objetivo con lo que el reconocimiento de voz convirtió a texto. Es útil para validar claridad global y palabras detectadas, pero no mide todavía fonemas, formantes, entonación, ritmo acústico ni posición de la lengua. No debe presentarse al usuario como una evaluación fonética clínica o certificada.
