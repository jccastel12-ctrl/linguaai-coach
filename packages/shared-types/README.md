# @linguaai/shared-types

Tipos TypeScript que reflejan los contratos de la API (`apps/api/app/domains/<dominio>/schemas.py`).

- Se consumen como código fuente TS (la web los transpila con `transpilePackages`).
- Uso: `import type { User, Lesson, CefrLevel } from "@linguaai/shared-types";`
- **Mantener sincronizados** con los esquemas Pydantic al cambiar la API. Plan: generarlos desde `/openapi.json` (ver ADR-001).

```bash
npm run typecheck --workspace @linguaai/shared-types
```
