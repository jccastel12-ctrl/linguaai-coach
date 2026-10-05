# LinguaAI Coach — Web

Frontend en Next.js 15 (App Router) + React 19 + TypeScript estricto.

## Ejecutar localmente

Desde la **raíz del monorepo** (usa npm workspaces):

```bash
npm install
cp apps/web/.env.local.example apps/web/.env.local
npm run dev:web          # http://localhost:3000
```

La web incluye registro/login, onboarding, dashboard, tutor de texto, historial, progreso y traductor ES/EN/SR. Las operaciones autenticadas pasan por Route Handlers de Next.js para mantener el JWT en cookie HttpOnly.

## Scripts

| Script | Descripción |
|--------|-------------|
| `npm run dev` | Servidor de desarrollo |
| `npm run build` | Build de producción (`output: standalone`) |
| `npm run start` | Sirve el build |
| `npm run lint` | ESLint (`next/core-web-vitals` + `next/typescript`) |
| `npm run typecheck` | `tsc --noEmit` |

## Estructura

```
src/
├── app/            rutas de producto y Route Handlers BFF
├── components/     auth, onboarding, tutor, translator y UI
├── lib/            cliente API, sesión server-side y helpers del tutor
└── types/index.ts  re-exporta @linguaai/shared-types
```

## Planes

La ruta `/plans` muestra Basic/Pro y, para usuarios autenticados, el consumo diario de Tutor, Traducción y Pronunciación. El botón Pro registra interés; no existe checkout ni cobro en v0.9.0.

## v1.0 — panel administrativo

`/admin` solo se muestra y permite cuando `/auth/me` devuelve `is_superuser=true`. La página consume la API mediante la misma cookie HttpOnly/BFF usada por el resto de la web y permite revisar usuarios, solicitudes Pro, estado de cuenta y auditoría.
